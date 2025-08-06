from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from .forms import UserActivationForm, ResendActivationForm

User = get_user_model()

# ========== نظام تفعيل الحساب ==========

class ActivationSentView(TemplateView):
    """صفحة تأكيد إرسال إيميل التفعيل"""
    template_name = 'accounts/activation_sent.html'


def activate_account_by_token(request, token):
    """تفعيل الحساب باستخدام الرابط المرسل في الإيميل"""
    try:
        user = get_object_or_404(User, activation_token=token)
        
        if user.is_email_verified:
            messages.info(request, 'حسابك مفعل بالفعل!')
            return redirect('accounts:login')
        
        if not user.is_activation_code_valid():
            messages.error(request, 'انتهت صلاحية رابط التفعيل. يرجى طلب رابط جديد.')
            return redirect('accounts:resend_activation')
        
        # تفعيل الحساب
        user.is_email_verified = True
        user.is_active = True
        user.activation_code = None
        user.activation_code_created = None
        user.save()
        
        messages.success(request, 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
        return redirect('accounts:login')
        
    except User.DoesNotExist:
        messages.error(request, 'رابط التفعيل غير صحيح.')
        return redirect('accounts:resend_activation')


class ActivateAccountView(FormView):
    """تفعيل الحساب باستخدام الكود"""
    template_name = 'accounts/activate.html'
    form_class = UserActivationForm
    success_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # يمكن إضافة معلومات إضافية هنا
        return context
    
    def form_valid(self, form):
        activation_code = form.cleaned_data['activation_code']
        
        # الحصول على الإيميل من الجلسة أو النموذج
        email = self.request.session.get('activation_email')
        if not email:
            # إذا لم يكن هناك إيميل في الجلسة، اطلب من المستخدم إدخاله
            messages.error(self.request, 'يرجى إدخال بريدك الإلكتروني أولاً.')
            return redirect('accounts:resend_activation')
        
        # البحث عن المستخدم بالإيميل (وليس بالكود!)
        try:
            user = User.objects.get(
                email=email,
                is_email_verified=False
            )
            
            if not user.is_activation_code_valid():
                messages.error(self.request, 'انتهت صلاحية كود التفعيل. يرجى طلب كود جديد.')
                return redirect('accounts:resend_activation')
            
            # تفعيل الحساب بالكود الصحيح
            if user.activate_account(activation_code):
                messages.success(self.request, 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
                # إزالة الإيميل من الجلسة بعد التفعيل الناجح
                if 'activation_email' in self.request.session:
                    del self.request.session['activation_email']
                return redirect(self.success_url)
            else:
                messages.error(self.request, 'كود التفعيل غير صحيح. يرجى التأكد من الكود المرسل إلى بريدك الإلكتروني.')
                
        except User.DoesNotExist:
            messages.error(self.request, 'لا يوجد حساب غير مفعل بهذا البريد الإلكتروني.')
        
        return self.form_invalid(form)


class ResendActivationView(FormView):
    """إعادة إرسال كود التفعيل"""
    template_name = 'accounts/resend_activation.html'
    form_class = ResendActivationForm
    success_url = reverse_lazy('accounts:activation_sent')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified:
                messages.info(self.request, 'حسابك مفعل بالفعل!')
                return redirect('accounts:login')
            
            # حفظ الإيميل في الجلسة لاستخدامه في التفعيل
            self.request.session['activation_email'] = email
            
            # إرسال إيميل التفعيل الجديد
            if user.send_activation_email(self.request):
                messages.success(self.request, 'تم إرسال كود التفعيل الجديد إلى بريدك الإلكتروني.')
                return redirect(self.success_url)
            else:
                messages.error(self.request, 'فشل في إرسال الإيميل. يرجى المحاولة مرة أخرى.')
                
        except User.DoesNotExist:
            messages.error(self.request, 'لا يوجد حساب مسجل بهذا البريد الإلكتروني.')
        
        return self.form_invalid(form)


def check_activation_status(request):
    """فحص حالة التفعيل للمستخدم الحالي"""
    if request.user.is_authenticated:
        if not request.user.is_email_verified:
            messages.warning(request, 'يرجى تفعيل حسابك عبر الرابط المرسل إلى بريدك الإلكتروني.')
            return redirect('accounts:activation_sent')
    return redirect('home:index')
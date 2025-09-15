from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'user_type')
        widgets = {
            'user_type': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control auth-form-input', 'placeholder': 'اسم المستخدم'})
        self.fields['email'].widget.attrs.update({'class': 'form-control auth-form-input', 'placeholder': 'البريد الإلكتروني'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control auth-form-input', 'placeholder': 'رقم الهاتف'})
        self.fields['user_type'].label = "اختر نوع الحساب"
        self.fields['password1'].widget.attrs.update({'class': 'form-control auth-form-input', 'placeholder': 'كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control auth-form-input', 'placeholder': 'تأكيد كلمة المرور'})


    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number")
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})


class UserActivationForm(forms.Form):
    """نموذج تفعيل الحساب باستخدام الكود"""
    activation_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;'
        }),
        label='كود التفعيل',
        help_text='أدخل الكود المكون من 6 أرقام المرسل إلى بريدك الإلكتروني'
    )
    
    def clean_activation_code(self):
        code = self.cleaned_data.get('activation_code')
        if not code.isdigit():
            raise ValidationError('كود التفعيل يجب أن يحتوي على أرقام فقط')
        return code


class ResendActivationForm(forms.Form):
    """نموذج إعادة إرسال كود التفعيل"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني'
        }),
        label='البريد الإلكتروني',
        help_text='أدخل البريد الإلكتروني المسجل به الحساب'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_email_verified:
                raise ValidationError('هذا الحساب مفعل بالفعل')
            return email
        except CustomUser.DoesNotExist:
            raise ValidationError('لا يوجد حساب مسجل ��هذا البريد الإلكتروني')

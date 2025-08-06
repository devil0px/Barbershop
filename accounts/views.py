from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView, FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import logging
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.utils import timezone
from django.db.models import Count, Q
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserActivationForm, ResendActivationForm
from barbershops.models import Barbershop, Service
from reviews.models import Review
from bookings.models import Booking

User = get_user_model()
logger = logging.getLogger(__name__)

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:activation_sent')

    def form_invalid(self, form):
        logger.error("Form is invalid")
        logger.error(form.errors.as_json())
        messages.error(self.request, 'الرجاء تصحيح الأخطاء أدناه.')
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.info("Form is valid, saving user...")
        user = form.save()
        
        # حفظ الإيميل في الجلسة لاستخدامه في التفعيل
        self.request.session['activation_email'] = user.email
        logger.info(f"Saved activation email to session: {user.email}")
        
        # إرسال إيميل التفعيل
        if user.send_activation_email(self.request):
            logger.info("Activation email sent successfully.")
            messages.success(self.request, 'تم إنشاء حسابك بنجاح! تم إرسال رابط التفعيل إلى بريدك الإلكتروني.')
        else:
            logger.error("Failed to send activation email.")
            messages.warning(self.request, 'تم إنشاء حسابك ولكن فشل في إرسال إيميل التفعيل. يمكنك طلب إعادة الإرسال.')
        
        return redirect(self.success_url)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

class DashboardView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.user_type == 'barber':
            return reverse_lazy('accounts:barber_dashboard')
        else:
            # العملاء يذهبون للصفحة الرئيسية لتصفح المحلات
            return reverse_lazy('barbershops:list')

class BarberDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/barber_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        # Get all barbershops owned by the user, ordered by creation date
        user_barbershops = Barbershop.objects.filter(owner=user).order_by('created_at')
        context['user_barbershops'] = user_barbershops
        
        # Pass the first barbershop to the context, if it exists
        primary_shop = user_barbershops.first()
        context['primary_shop'] = primary_shop

        if primary_shop:
            # Get recent bookings for the primary shop
            recent_bookings = Booking.objects.filter(
                barbershop=primary_shop
            ).select_related('customer', 'service').order_by('-created_at')[:5]
            context['recent_bookings'] = recent_bookings

            # Get current turn number - استخدام الدور المحفوظ في المحل لضمان التطابق
            context['current_turn_number'] = primary_shop.current_turn_number if primary_shop.current_turn_number > 0 else None

            # Get finished bookings count for today
            context['finished_bookings_count'] = Booking.objects.filter(
                barbershop=primary_shop,
                booking_day=today,
                status__in=['completed', 'no_show']
            ).count()

            # Get recent reviews
            recent_reviews = Review.objects.filter(
                barbershop=primary_shop,
                is_approved=True
            ).select_related('customer').order_by('-created_at')[:3]
            context['recent_reviews'] = recent_reviews
        else:
            context['recent_bookings'] = []
            context['current_turn_number'] = None
            context['finished_bookings_count'] = 0
            context['recent_reviews'] = []

        context['today'] = today

        return context

class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/customer_dashboard.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('accounts:password_change_done')

class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'


#

from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    RegisterView, 
    CustomLoginView, 
    DashboardView,
    BarberDashboardView,
    CustomerDashboardView,
    ProfileView, 
    EditProfileView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView
)
from .activation_views import (
    ActivationSentView,
    ActivateAccountView,
    ResendActivationView,
    activate_account_by_token,
    check_activation_status
)
from .google_views import (
    google_one_tap_login,
    google_login_status,
    google_logout
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/barber/', BarberDashboardView.as_view(), name='barber_dashboard'),
    path('dashboard/customer/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # نظام تفعيل الحساب
    path('activation/sent/', ActivationSentView.as_view(), name='activation_sent'),
    path('activate/', ActivateAccountView.as_view(), name='activate_code'),
    path('activate/<uuid:token>/', activate_account_by_token, name='activate'),
    path('resend-activation/', ResendActivationView.as_view(), name='resend_activation'),
    path('check-activation/', check_activation_status, name='check_activation'),
    
    # Google OAuth و One Tap Sign-In
    path('google/one-tap/', google_one_tap_login, name='google_one_tap'),
    path('google/status/', google_login_status, name='google_status'),
    path('google/logout/', google_logout, name='google_logout'),
]

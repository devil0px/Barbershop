from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('confirm/<int:pk>/', views.BookingConfirmView.as_view(), name='confirm'),
    # Customer booking URLs
    path('', views.CustomerBookingListView.as_view(), name='list'),
    path('create/<int:barbershop_id>/', views.BookingCreateView.as_view(), name='create_booking'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BookingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BookingDeleteView.as_view(), name='delete'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('<int:pk>/chat/', views.BookingChatView.as_view(), name='booking_chat'),

    
    # Merchant booking management URLs
    path('merchant/', views.MerchantBookingRedirectView.as_view(), name='merchant_redirect'),
    path('merchant/<int:barbershop_id>/', views.MerchantBookingListView.as_view(), name='merchant_list'),
    path('merchant/<int:pk>/', views.BookingDetailView.as_view(), name='merchant_detail'),
    path('merchant/<int:pk>/update-status/', views.BookingUpdateStatusView.as_view(), name='update_status'),
    path('merchant/<int:pk>/confirm/', views.BookingConfirmView.as_view(), name='confirm'),
    path('merchant/<int:pk>/reject/', views.BookingRejectView.as_view(), name='reject'),
    path('merchant/<int:pk>/completed/', views.BookingCompletedView.as_view(), name='completed'),
    path('merchant/<int:pk>/no-show/', views.BookingNoShowView.as_view(), name='no_show'),

    path('merchant/<int:pk>/chat/', views.BookingChatView.as_view(), name='merchant_chat'),
    path('merchant/search/', views.BookingSearchView.as_view(), name='search'),
    path('merchant/today/', views.TodayBookingsView.as_view(), name='today'),
]
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='edit'),
    path('merchant/', views.MerchantReviewListView.as_view(), name='merchant_list'),
    path('', views.ReviewListView.as_view(), name='list'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='detail'),
    path('create/<int:barbershop_id>/', views.ReviewCreateView.as_view(), name='create'),
    path('barbershop/<int:barbershop_id>/', views.BarbershopReviewListView.as_view(), name='barbershop_reviews'),
]
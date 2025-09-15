from django.urls import path
from . import views

app_name = 'barbershops'

urlpatterns = [
    # Barbershop URLs
    path('', views.BarbershopListView.as_view(), name='list'),
    path('my-barbershops/', views.MyBarbershopsListView.as_view(), name='my_list'),
    path('nearby/', views.NearbyBarbershopsView.as_view(), name='nearby'),
    path('api/nearby/', views.NearbyBarbershopsAPIView.as_view(), name='api_nearby'),
    path('create/', views.BarbershopCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BarbershopDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BarbershopUpdateView.as_view(), name='edit'),
    
    # Service Management URLs
    path('<int:barbershop_pk>/services/', views.ServiceListView.as_view(), name='service_list'),
    path('<int:barbershop_pk>/services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    # Review URLs
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('reviews/<int:pk>/reply/', views.ReviewReplyView.as_view(), name='review_reply'),
]
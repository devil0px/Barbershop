from django.urls import path
from .safe_views import SafeHomePageView
from .simple_views import simple_home_view

app_name = 'home'

urlpatterns = [
    path('', SafeHomePageView.as_view(), name='index'),
    path('simple/', simple_home_view, name='simple'),
]
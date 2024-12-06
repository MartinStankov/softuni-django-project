from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView, settings


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('settings/', settings, name='settings')
]

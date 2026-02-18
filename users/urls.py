# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    # Регистрация
    path('register/', views.register, name='register'),

    # Вход с кастомной формой
    path('login/',
         auth_views.LoginView.as_view(
             template_name='users/login.html',
             authentication_form=CustomLoginForm,
             redirect_authenticated_user=True
         ),
         name='login'),

    # Выход - ИСПРАВЛЕНО!
    path('logout/',
         LogoutView.as_view(
             next_page='home'  # явно указываем, куда переходить после выхода
         ),
         name='logout'),

    # Профиль и избранное
    path('profile/', views.profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('notifications/', views.notification_settings, name='notification_settings'),
]
# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_read'),
    path('read-all/', views.mark_all_as_read, name='mark_all_read'),
    path('settings/', views.notification_settings, name='settings'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
]
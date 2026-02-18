# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Список отчётов
    path('', views.report_list, name='list'),

    # Генерация нового отчёта
    path('generate/', views.generate_report, name='generate'),

    # Скачивание отчёта
    path('<int:pk>/download/', views.download_report, name='download'),

    # Удаление отчёта
    path('<int:pk>/delete/', views.delete_report, name='delete'),

    # Запланированные отчёты
    path('scheduled/', views.scheduled_reports, name='scheduled'),
    path('scheduled/create/', views.create_scheduled_report, name='schedule_create'),
    path('scheduled/<int:pk>/toggle/', views.toggle_scheduled_report, name='schedule_toggle'),
    path('scheduled/<int:pk>/delete/', views.delete_scheduled_report, name='schedule_delete'),
]
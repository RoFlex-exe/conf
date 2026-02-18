# organizations/urls.py
from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Список организаций
    path('', views.OrganizationListView.as_view(), name='organization_list'),

    # Детальная страница организации
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='organization_detail'),

    # Избранное для организаций
    path('<int:pk>/favorite/', views.toggle_favorite_org, name='toggle_favorite_org'),

    # Личный кабинет организации
    path('dashboard/', views.organization_dashboard, name='dashboard'),

    # Профиль организации
    path('profile/', views.organization_profile, name='organization_profile'),

    # Управление конференциями
    path('conferences/', views.organization_conferences, name='org_conferences'),
    path('conferences/create/', views.create_conference, name='create_conference'),
    path('conferences/<int:pk>/edit/', views.edit_conference, name='edit_conference'),
    path('conferences/<int:pk>/delete/', views.delete_conference, name='delete_conference'),

    # Управление заявками
    path('applications/', views.organization_applications, name='org_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/update/', views.update_application_status, name='update_application'),

    # Статистика
    path('statistics/', views.organization_statistics, name='org_statistics'),
]
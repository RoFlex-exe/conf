# conferences/urls.py
from django.urls import path
from . import views

app_name = 'conferences'

urlpatterns = [
    # Список конференций (с фильтрацией)
    path('', views.ConferenceListView.as_view(), name='conference_list'),

    # Мои заявки
    path('my-applications/', views.my_applications, name='my_applications'),

    # Отмена заявки
    path('application/<int:pk>/cancel/', views.cancel_application, name='cancel_application'),

    # Детальная страница конференции (по slug)
    path('<slug:slug>/', views.ConferenceDetailView.as_view(), name='conference_detail'),

    # Добавление/удаление из избранного (через POST)
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),

    # Подача заявки на участие
    path('<slug:slug>/apply/', views.apply_to_conference, name='apply_to_conference'),

    # Отзывы
    path('<slug:slug>/review/', views.add_review, name='add_review'),

    # Фильтрация по тематике
    path('topic/<slug:topic_slug>/', views.ConferenceByTopicView.as_view(), name='by_topic'),
]
# conf_promotion/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Приложение users
    path('users/', include('users.urls')),

    # Приложение conferences - все маршруты начинаются с /conferences/
    path('conferences/', include('conferences.urls')),

    # Приложение organizations - все маршруты начинаются с /organizations/
    path('organizations/', include('organizations.urls')),

    # Главная страница (core)
    path('', include('core.urls')),

    path('notifications/', include('notifications.urls')),

    path('reports/', include('reports.urls')),
]

# Для обслуживания медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# notifications/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification, NotificationSettings


@login_required
def notification_list(request):
    """
    Список всех уведомлений пользователя
    """
    notifications = Notification.objects.filter(user=request.user)

    # Фильтрация по статусу
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)

    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    notifications_page = paginator.get_page(page)

    # Статистика
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'notifications/list.html', {
        'notifications': notifications_page,
        'unread_count': unread_count,
        'current_filter': filter_type,
    })


@login_required
@require_POST
def mark_as_read(request, pk):
    """
    Отметить уведомление как прочитанное
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_as_read(request):
    """
    Отметить все уведомления как прочитанные
    """
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    messages.success(request, 'Все уведомления отмечены как прочитанные')
    return redirect('notifications:list')


@login_required
def notification_settings(request):
    """
    Настройки уведомлений
    """
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings.notify_deadline = request.POST.get('notify_deadline') == 'on'
        settings.notify_application = request.POST.get('notify_application') == 'on'
        settings.notify_new_conference = request.POST.get('notify_new_conference') == 'on'
        settings.notify_favorite_org = request.POST.get('notify_favorite_org') == 'on'
        settings.notify_reminder = request.POST.get('notify_reminder') == 'on'
        settings.send_weekly_digest = request.POST.get('send_weekly_digest') == 'on'
        settings.send_email = request.POST.get('send_email') == 'on'
        settings.send_site = request.POST.get('send_site') == 'on'
        settings.save()

        messages.success(request, 'Настройки уведомлений сохранены')
        return redirect('notifications:settings')

    return render(request, 'notifications/settings.html', {
        'settings': settings
    })


@login_required
def get_unread_count(request):
    """
    AJAX-запрос для получения количества непрочитанных уведомлений
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})
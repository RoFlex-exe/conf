# core/views.py
from django.shortcuts import render
from django.db.models import Count, Q, Avg
from datetime import date, timedelta
from conferences.models import Conference, Topic
from organizations.models import Organization


def index(request):
    """
    Главная страница с рекомендациями и статистикой
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)

    # Статистика
    total_conferences = Conference.objects.filter(status=Conference.Status.PUBLISHED).count()
    total_organizations = Organization.objects.filter(is_active=True, is_verified=True).count()
    upcoming_count = Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        start_date__gte=today
    ).count()

    # Ближайшие конференции (следующие 7 дней)
    upcoming_conferences = Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        start_date__gte=today,
        start_date__lte=next_week
    ).select_related('organization').order_by('start_date')[:6]

    # Рекомендуемые конференции
    featured_conferences = Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        is_featured=True,
        start_date__gte=today
    ).select_related('organization').order_by('start_date')[:6]

    # Популярные конференции (по просмотрам)
    popular_conferences = Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        start_date__gte=today
    ).order_by('-view_count')[:6]

    # Конференции с ближайшим дедлайном
    deadline_conferences = Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        deadline__gte=today,
        deadline__lte=next_month
    ).order_by('deadline')[:6]

    # Активные организации
    active_organizations = Organization.objects.filter(
        is_active=True,
        is_verified=True
    ).annotate(
        conf_count=Count('conferences', filter=Q(conferences__status=Conference.Status.PUBLISHED))
    ).filter(conf_count__gt=0).order_by('-conf_count')[:8]

    # Популярные тематики
    popular_topics = Topic.objects.filter(
        is_active=True,
        conferences__status=Conference.Status.PUBLISHED
    ).annotate(
        conf_count=Count('conferences', filter=Q(conferences__status=Conference.Status.PUBLISHED))
    ).filter(conf_count__gt=0).order_by('-conf_count')[:10]

    # Персонализированные рекомендации (если пользователь авторизован)
    recommended_conferences = []
    if request.user.is_authenticated and hasattr(request.user, 'interests'):
        user_interests = request.user.interests.all()
        if user_interests:
            recommended_conferences = Conference.objects.filter(
                status=Conference.Status.PUBLISHED,
                topics__in=user_interests,
                start_date__gte=today
            ).distinct().order_by('start_date')[:6]

    context = {
        'total_conferences': total_conferences,
        'total_organizations': total_organizations,
        'upcoming_count': upcoming_count,
        'upcoming_conferences': upcoming_conferences,
        'featured_conferences': featured_conferences,
        'popular_conferences': popular_conferences,
        'deadline_conferences': deadline_conferences,
        'active_organizations': active_organizations,
        'popular_topics': popular_topics,
        'recommended_conferences': recommended_conferences,
        'today': today,
    }

    return render(request, 'core/index.html', context)
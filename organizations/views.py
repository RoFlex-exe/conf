# organizations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import date, timedelta
from .models import Organization, OrganizationDocument
from conferences.models import Conference, ConferenceApplication, Topic
from notifications.models import Notification
from .forms import ConferenceForm, ConferenceApplicationStatusForm
from django.core.paginator import Paginator
from collections import Counter


class OrganizationListView(ListView):
    """
    Список всех организаций
    """
    model = Organization
    template_name = 'organizations/organization_list.html'
    context_object_name = 'organizations'
    paginate_by = 12

    def get_queryset(self):
        queryset = Organization.objects.filter(is_active=True, is_verified=True)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(short_name__icontains=q) |
                Q(description__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_organizations'] = Organization.objects.filter(
            is_active=True, is_verified=True
        ).count()
        return context


class OrganizationDetailView(DetailView):
    """
    Детальная страница организации
    """
    model = Organization
    template_name = 'organizations/organization_detail.html'
    context_object_name = 'organization'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_object()

        context['conferences'] = Conference.objects.filter(
            organization=organization,
            status=Conference.Status.PUBLISHED
        ).order_by('-start_date')[:5]

        all_conferences = Conference.objects.filter(organization=organization)
        context['total_conferences'] = all_conferences.count()
        context['upcoming_conferences'] = all_conferences.filter(
            start_date__gte=date.today()
        ).count()
        context['past_conferences'] = all_conferences.filter(
            end_date__lt=date.today()
        ).count()

        if self.request.user.is_authenticated:
            context['is_favorite'] = organization.favorited_by.filter(
                user=self.request.user
            ).exists()

        return context


@login_required
def organization_dashboard(request):
    """
    Личный кабинет организации
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа к панели организации')
        return redirect('home')

    if not organization.is_active:
        messages.warning(request, 'Договор с организацией не активен. Доступ ограничен.')
        return redirect('home')

    conferences = Conference.objects.filter(organization=organization)
    today = date.today()

    applications = ConferenceApplication.objects.filter(
        conference__in=conferences
    ).select_related('conference', 'user')

    context = {
        'organization': organization,
        'total_conferences': conferences.count(),
        'published_conferences': conferences.filter(status=Conference.Status.PUBLISHED).count(),
        'pending_conferences': conferences.filter(status=Conference.Status.PENDING).count(),
        'draft_conferences': conferences.filter(status=Conference.Status.DRAFT).count(),
        'recent_conferences': conferences.order_by('-created_at')[:5],
        'total_applications': applications.count(),
        'new_applications': applications.filter(status='new').count(),
        'total_views': conferences.aggregate(Sum('view_count'))['view_count__sum'] or 0,
        'upcoming_conferences': conferences.filter(start_date__gte=today).count(),
        'recent_applications': applications.order_by('-created_at')[:10],
    }

    return render(request, 'organizations/dashboard.html', context)


@login_required
def organization_conferences(request):
    """
    Управление мероприятиями организации
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    status_filter = request.GET.get('status', 'all')

    conferences = Conference.objects.filter(organization=organization)

    if status_filter != 'all':
        conferences = conferences.filter(status=status_filter)

    conferences = conferences.order_by('-created_at')

    status_counts = {
        'all': Conference.objects.filter(organization=organization).count(),
        'published': Conference.objects.filter(organization=organization, status=Conference.Status.PUBLISHED).count(),
        'pending': Conference.objects.filter(organization=organization, status=Conference.Status.PENDING).count(),
        'draft': Conference.objects.filter(organization=organization, status=Conference.Status.DRAFT).count(),
        'archived': Conference.objects.filter(organization=organization, status=Conference.Status.ARCHIVED).count(),
        'rejected': Conference.objects.filter(organization=organization, status=Conference.Status.REJECTED).count(),
    }

    paginator = Paginator(conferences, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'organizations/conferences.html', {
        'organization': organization,
        'conferences': page_obj,
        'status_counts': status_counts,
        'current_status': status_filter,
    })


# organizations/views.py (фрагмент с create_conference)

@login_required
def create_conference(request):
    """
    Создание нового мероприятия
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа к созданию мероприятий')
        return redirect('home')

    if not organization.is_active:
        messages.error(request, 'Организация не активна')
        return redirect('organizations:dashboard')

    total_conferences = Conference.objects.filter(organization=organization).count()

    if request.method == 'POST':
        form = ConferenceForm(request.POST, request.FILES)
        if form.is_valid():
            conference = form.save(commit=False)
            conference.organization = organization

            # Если пользователь не суперпользователь, отправляем на модерацию
            if not request.user.is_superuser:
                conference.status = Conference.Status.PENDING

            conference.save()
            form.save_m2m()  # Сохраняем ManyToMany поля (topics)

            messages.success(request, f'Мероприятие "{conference.title}" успешно создано!')

            if conference.status == Conference.Status.PENDING:
                messages.info(request, 'Мероприятие отправлено на модерацию. После проверки оно будет опубликовано.')

            return redirect('organizations:org_conferences')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        # Предзаполняем поля данными организации
        initial_data = {
            'contact_email': organization.contact_email,
            'contact_phone': organization.contact_phone,
            'contact_person': organization.contact_person,
        }
        form = ConferenceForm(initial=initial_data)

    topics = Topic.objects.filter(is_active=True).order_by('name')

    return render(request, 'organizations/create_conference.html', {
        'organization': organization,
        'form': form,
        'topics': topics,
        'total_conferences': total_conferences,
    })


@login_required
def edit_conference(request, pk):
    """
    Редактирование мероприятия
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    conference = get_object_or_404(Conference, pk=pk, organization=organization)
    total_conferences = Conference.objects.filter(organization=organization).count()

    if request.method == 'POST':
        form = ConferenceForm(request.POST, request.FILES, instance=conference)
        if form.is_valid():
            edited_conference = form.save(commit=False)

            # Если конференция была опубликована и её редактируют, отправляем на модерацию
            if conference.status == Conference.Status.PUBLISHED and not request.user.is_superuser:
                edited_conference.status = Conference.Status.PENDING
                messages.warning(request, 'Мероприятие отправлено на повторную модерацию после изменений.')

            # Обработка удаления постера
            if request.POST.get('poster_clear') == 'on':
                edited_conference.poster.delete(save=False)
                edited_conference.poster = None

            edited_conference.save()
            form.save_m2m()  # Сохраняем ManyToMany поля (topics)

            messages.success(request, f'Мероприятие "{conference.title}" успешно обновлено!')
            return redirect('organizations:org_conferences')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ConferenceForm(instance=conference)

    topics = Topic.objects.filter(is_active=True).order_by('name')

    return render(request, 'organizations/edit_conference.html', {
        'organization': organization,
        'conference': conference,
        'form': form,
        'topics': topics,
        'total_conferences': total_conferences,
    })


@login_required
def delete_conference(request, pk):
    """
    Удаление мероприятия
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    conference = get_object_or_404(Conference, pk=pk, organization=organization)
    total_conferences = Conference.objects.filter(organization=organization).count()

    if request.method == 'POST':
        conference_title = conference.title
        conference.delete()
        messages.success(request, f'Мероприятие "{conference_title}" удалено')
        return redirect('organizations:org_conferences')

    return render(request, 'organizations/delete_conference.html', {
        'organization': organization,
        'conference': conference,
        'total_conferences': total_conferences,
    })


@login_required
def organization_applications(request):
    """
    Заявки на мероприятия организации
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    applications = ConferenceApplication.objects.filter(
        conference__organization=organization
    ).select_related('conference', 'user').order_by('-created_at')

    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        applications = applications.filter(status=status_filter)

    conference_filter = request.GET.get('conference')
    if conference_filter:
        applications = applications.filter(conference_id=conference_filter)

    search_query = request.GET.get('q')
    if search_query:
        applications = applications.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(presentation_title__icontains=search_query)
        )

    status_counts = {
        'all': applications.count(),
        'new': applications.filter(status='new').count(),
        'under_review': applications.filter(status='under_review').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
        'confirmed': applications.filter(status='confirmed').count(),
        'cancelled': applications.filter(status='cancelled').count(),
    }

    conferences = Conference.objects.filter(organization=organization)

    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'organizations/applications.html', {
        'organization': organization,
        'applications': page_obj,
        'status_counts': status_counts,
        'current_status': status_filter,
        'conferences': conferences,
        'current_conference': conference_filter,
        'search_query': search_query or '',
    })


@login_required
def application_detail(request, pk):
    """
    Детальный просмотр заявки
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    application = get_object_or_404(
        ConferenceApplication,
        pk=pk,
        conference__organization=organization
    )

    if request.method == 'POST':
        form = ConferenceApplicationStatusForm(request.POST)
        if form.is_valid():
            old_status = application.status
            new_status = form.cleaned_data['status']

            application.status = new_status
            application.organizer_comment = form.cleaned_data['organizer_comment']

            # Если статус меняется на "подтверждена", добавляем ссылку на встречу
            if new_status == 'confirmed':
                meeting_link = form.cleaned_data.get('meeting_link', '')
                if meeting_link:
                    application.meeting_link = meeting_link

                # Создаём уведомление для участника
                Notification.objects.create(
                    user=application.user,
                    notification_type='application',
                    title='Ваша заявка подтверждена',
                    message=f'Ваша заявка на участие в мероприятии "{application.conference.title}" подтверждена.',
                    conference=application.conference
                )

                # Если участник выбрал дистанционный формат, отправляем ссылку
                if application.participation_format == 'online' and meeting_link:
                    Notification.objects.create(
                        user=application.user,
                        notification_type='application',
                        title='Ссылка для подключения',
                        message=f'Ссылка для дистанционного участия: {meeting_link}',
                        conference=application.conference
                    )

            application.save()
            messages.success(request, f'Статус заявки изменён на "{application.get_status_display()}"')
            return redirect('organizations:application_detail', pk=application.pk)
    else:
        form = ConferenceApplicationStatusForm(initial={
            'status': application.status,
            'organizer_comment': application.organizer_comment,
            'meeting_link': application.meeting_link or application.conference.online_meeting_link,
        })

    return render(request, 'organizations/application_detail.html', {
        'organization': organization,
        'application': application,
        'form': form,
        'application_status_choices': ConferenceApplication.ApplicationStatus.choices,
    })


@login_required
def update_application_status(request, pk):
    """
    Быстрое обновление статуса заявки
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    application = get_object_or_404(
        ConferenceApplication,
        pk=pk,
        conference__organization=organization
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment = request.POST.get('organizer_comment', '')
        meeting_link = request.POST.get('meeting_link', '')

        if new_status in dict(ConferenceApplication.ApplicationStatus.choices):
            old_status = application.status
            application.status = new_status
            if comment:
                application.organizer_comment = comment

            if new_status == 'confirmed' and meeting_link:
                application.meeting_link = meeting_link

                Notification.objects.create(
                    user=application.user,
                    notification_type='application',
                    title='Ваша заявка подтверждена',
                    message=f'Ваша заявка на участие в мероприятии "{application.conference.title}" подтверждена.',
                    conference=application.conference
                )

                if application.participation_format == 'online' and meeting_link:
                    Notification.objects.create(
                        user=application.user,
                        notification_type='application',
                        title='Ссылка для подключения',
                        message=f'Ссылка для дистанционного участия: {meeting_link}',
                        conference=application.conference
                    )

            application.save()
            messages.success(request, f'Статус заявки изменён на "{application.get_status_display()}"')
        else:
            messages.error(request, 'Некорректный статус')

    return redirect(request.META.get('HTTP_REFERER', 'organizations:org_applications'))


@login_required
def organization_statistics(request):
    """
    Детальная статистика для организации
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    conferences = Conference.objects.filter(organization=organization)
    today = date.today()

    total_conferences = conferences.count()
    total_views = conferences.aggregate(Sum('view_count'))['view_count__sum'] or 0
    total_favorites = conferences.aggregate(Sum('favorites_count'))['favorites_count__sum'] or 0
    total_applications = conferences.aggregate(Sum('applications_count'))['applications_count__sum'] or 0

    avg_views = total_views / total_conferences if total_conferences else 0
    avg_applications = total_applications / total_conferences if total_conferences else 0

    status_stats = {
        'published': conferences.filter(status=Conference.Status.PUBLISHED).count(),
        'pending': conferences.filter(status=Conference.Status.PENDING).count(),
        'draft': conferences.filter(status=Conference.Status.DRAFT).count(),
        'archived': conferences.filter(status=Conference.Status.ARCHIVED).count(),
        'rejected': conferences.filter(status=Conference.Status.REJECTED).count(),
    }

    # Статистика по типам мероприятий
    type_stats = {}
    for type_code, type_name in Conference.EventType.choices:
        count = conferences.filter(event_type=type_code).count()
        if count > 0:
            type_stats[type_name] = count

    # Статистика по форматам
    format_stats = {}
    for format_code, format_name in Conference.Format.choices:
        count = conferences.filter(format=format_code).count()
        if count > 0:
            format_stats[format_name] = count

    # Топ мероприятий
    top_by_views = conferences.order_by('-view_count')[:5]
    top_by_favorites = conferences.order_by('-favorites_count')[:5]
    top_by_applications = conferences.order_by('-applications_count')[:5]

    # Статистика по тематикам
    topic_stats = []
    for conference in conferences:
        for topic in conference.topics.all():
            topic_stats.append(topic.name)

    topic_counter = Counter(topic_stats).most_common(10)

    context = {
        'organization': organization,
        'total_conferences': total_conferences,
        'total_views': total_views,
        'total_favorites': total_favorites,
        'total_applications': total_applications,
        'avg_views': round(avg_views, 1),
        'avg_applications': round(avg_applications, 1),
        'status_stats': status_stats,
        'type_stats': type_stats,
        'format_stats': format_stats,
        'top_by_views': top_by_views,
        'top_by_favorites': top_by_favorites,
        'top_by_applications': top_by_applications,
        'topic_stats': topic_counter,
    }

    return render(request, 'organizations/statistics.html', context)


@login_required
def organization_profile(request):
    """
    Редактирование профиля организации (без логотипа)
    """
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'У вас нет доступа')
        return redirect('home')

    if request.method == 'POST':
        # Обновляем только текстовые поля, логотип не трогаем
        organization.contact_person = request.POST.get('contact_person', organization.contact_person)
        organization.contact_position = request.POST.get('contact_position', organization.contact_position)
        organization.contact_email = request.POST.get('contact_email', organization.contact_email)
        organization.contact_phone = request.POST.get('contact_phone', organization.contact_phone)
        organization.website = request.POST.get('website', organization.website)
        organization.description = request.POST.get('description', organization.description)

        # Логотип НЕ обновляем - это делает только администратор
        # if 'logo' in request.FILES:
        #     organization.logo = request.FILES['logo']

        organization.save()
        messages.success(request, 'Профиль организации обновлён')
        return redirect('organizations:dashboard')

    return render(request, 'organizations/profile.html', {
        'organization': organization
    })


# organizations/views.py - добавь эту функцию

@login_required
def toggle_favorite_org(request, pk):
    """
    Добавление/удаление организации из избранного
    """
    from conferences.models import FavoriteOrganization

    organization = get_object_or_404(Organization, pk=pk, is_active=True)

    if request.method == 'POST':
        favorite = FavoriteOrganization.objects.filter(
            user=request.user,
            organization=organization
        ).first()

        if favorite:
            favorite.delete()
            messages.success(request, f'Организация "{organization.name}" удалена из избранного')
        else:
            FavoriteOrganization.objects.create(
                user=request.user,
                organization=organization
            )
            messages.success(request, f'Организация "{organization.name}" добавлена в избранное')

    return redirect('organizations:organization_detail', pk=organization.pk)
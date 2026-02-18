# conferences/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import date
from .models import Conference, Topic, ConferenceReview, ConferenceApplication
from .forms import ConferenceApplicationForm, ConferenceReviewForm


class ConferenceListView(ListView):
    """
    Список всех конференций с фильтрацией
    """
    model = Conference
    template_name = 'conferences/conference_list.html'
    context_object_name = 'conferences'
    paginate_by = 10

    def get_queryset(self):
        """
        Фильтрация конференций по параметрам запроса
        """
        queryset = Conference.objects.filter(status=Conference.Status.PUBLISHED)

        # Поиск по названию
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(short_title__icontains=q)
            )

        # Фильтр по тематике
        topic = self.request.GET.get('topic')
        if topic:
            queryset = queryset.filter(topics__slug=topic)

        # Фильтр по типу конференции
        conf_type = self.request.GET.get('type')
        if conf_type:
            queryset = queryset.filter(conference_type=conf_type)

        # Фильтр по формату
        format = self.request.GET.get('format')
        if format:
            queryset = queryset.filter(format=format)

        # Фильтр по статусу (предстоящие/прошедшие)
        period = self.request.GET.get('period')
        today = date.today()
        if period == 'upcoming':
            queryset = queryset.filter(start_date__gte=today)
        elif period == 'past':
            queryset = queryset.filter(end_date__lt=today)
        elif period == 'ongoing':
            queryset = queryset.filter(start_date__lte=today, end_date__gte=today)

        # Сортировка
        sort = self.request.GET.get('sort', '-start_date')
        if sort in ['start_date', '-start_date', 'title', '-title', 'deadline', '-deadline']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляем дополнительные данные в контекст
        """
        context = super().get_context_data(**kwargs)

        # Все тематики для фильтра
        context['topics'] = Topic.objects.filter(is_active=True)

        # Текущие параметры фильтрации для подсветки в шаблоне
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'topic': self.request.GET.get('topic', ''),
            'type': self.request.GET.get('type', ''),
            'format': self.request.GET.get('format', ''),
            'period': self.request.GET.get('period', ''),
            'sort': self.request.GET.get('sort', '-start_date'),
        }

        # Статистика
        today = date.today()
        context['total_conferences'] = Conference.objects.filter(status=Conference.Status.PUBLISHED).count()
        context['upcoming_count'] = Conference.objects.filter(
            status=Conference.Status.PUBLISHED,
            start_date__gte=today
        ).count()

        return context


class ConferenceDetailView(DetailView):
    """
    Детальная страница конференции
    """
    model = Conference
    template_name = 'conferences/conference_detail.html'
    context_object_name = 'conference'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """
        Показываем только опубликованные конференции,
        но организаторы видят свои даже неопубликованные
        """
        queryset = Conference.objects.all()

        # Если пользователь не авторизован или не организатор, показываем только опубликованные
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status=Conference.Status.PUBLISHED)
        else:
            # Проверяем, является ли пользователь организатором
            try:
                org = self.request.user.organization
                # Если это организатор, показываем все его конференции
                queryset = queryset.filter(
                    Q(status=Conference.Status.PUBLISHED) |
                    Q(organization=org)
                )
            except:
                # Обычный пользователь - только опубликованные
                queryset = queryset.filter(status=Conference.Status.PUBLISHED)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляем дополнительные данные
        """
        context = super().get_context_data(**kwargs)

        # Увеличиваем счетчик просмотров (только для опубликованных)
        conference = self.get_object()
        if conference.status == Conference.Status.PUBLISHED:
            conference.view_count += 1
            conference.save(update_fields=['view_count'])

        # Похожие конференции (по тематикам)
        context['similar_conferences'] = Conference.objects.filter(
            status=Conference.Status.PUBLISHED,
            topics__in=conference.topics.all()
        ).exclude(id=conference.id).distinct()[:3]

        # Проверка, добавил ли пользователь в избранное
        if self.request.user.is_authenticated:
            context['is_favorite'] = conference.favorited_by.filter(
                user=self.request.user
            ).exists()

            # Проверил, оставлял ли пользователь отзыв
            context['user_review'] = conference.reviews.filter(
                user=self.request.user
            ).first()

            # Проверил, подавал ли пользователь заявку
            context['user_application'] = conference.applications.filter(
                user=self.request.user
            ).first()

        # Средний рейтинг
        avg_rating = conference.reviews.aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        context['reviews_count'] = conference.reviews.count()

        # Все отзывы
        context['reviews'] = conference.reviews.filter(is_published=True).order_by('-created_at')

        # Форма для отзыва (если пользователь авторизован и ещё не оставлял отзыв)
        if self.request.user.is_authenticated and not context.get('user_review'):
            context['review_form'] = ConferenceReviewForm()

        # Проверка, может ли пользователь редактировать (для организаторов)
        if self.request.user.is_authenticated:
            try:
                org = self.request.user.organization
                context['can_edit'] = (org == conference.organization)
            except:
                context['can_edit'] = False

        return context


@login_required
def toggle_favorite(request, pk):
    """
    Добавление/удаление конференции из избранного
    """
    conference = get_object_or_404(Conference, pk=pk, status=Conference.Status.PUBLISHED)

    if request.method == 'POST':
        favorite = conference.favorited_by.filter(user=request.user).first()

        if favorite:
            # Удаляем из избранного
            favorite.delete()
            conference.favorites_count -= 1
            conference.save(update_fields=['favorites_count'])
            messages.success(request, f'Конференция "{conference.title}" удалена из избранного')
        else:
            # Добавляем в избранное
            conference.favorited_by.create(user=request.user)
            conference.favorites_count += 1
            conference.save(update_fields=['favorites_count'])
            messages.success(request, f'Конференция "{conference.title}" добавлена в избранное')

    return redirect('conferences:conference_detail', slug=conference.slug)


@login_required
def apply_to_conference(request, slug):
    """
    Подача заявки на участие в конференции
    """
    conference = get_object_or_404(Conference, slug=slug, status=Conference.Status.PUBLISHED)

    # Проверяем, не подавал ли пользователь уже заявку
    existing_application = ConferenceApplication.objects.filter(
        user=request.user,
        conference=conference
    ).first()

    if existing_application:
        messages.warning(request, 'Вы уже подали заявку на эту конференцию')
        return redirect('conferences:conference_detail', slug=conference.slug)

    if request.method == 'POST':
        form = ConferenceApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.conference = conference
            application.save()

            # Увеличиваем счетчик заявок
            conference.applications_count += 1
            conference.save(update_fields=['applications_count'])

            messages.success(request, 'Заявка успешно отправлена! Оргкомитет свяжется с вами.')
            return redirect('conferences:conference_detail', slug=conference.slug)
    else:
        # Предзаполняем форму данными из профиля
        initial_data = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'organization': request.user.affiliation,
            'academic_degree': request.user.get_academic_degree_display() if request.user.academic_degree else '',
        }
        form = ConferenceApplicationForm(initial=initial_data)

    return render(request, 'conferences/apply.html', {
        'conference': conference,
        'form': form
    })


@login_required
def add_review(request, slug):
    """
    Добавление отзыва на конференцию
    """
    conference = get_object_or_404(Conference, slug=slug, status=Conference.Status.PUBLISHED)

    # Проверяем, не оставлял ли пользователь уже отзыв
    existing_review = ConferenceReview.objects.filter(
        user=request.user,
        conference=conference
    ).first()

    if existing_review:
        messages.warning(request, 'Вы уже оставляли отзыв на эту конференцию')
        return redirect('conferences:conference_detail', slug=conference.slug)

    if request.method == 'POST':
        form = ConferenceReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.conference = conference

            # Проверяем, участвовал ли пользователь в конференции
            has_applied = ConferenceApplication.objects.filter(
                user=request.user,
                conference=conference,
                status='confirmed'
            ).exists()

            if has_applied:
                review.is_verified = True

            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('conferences:conference_detail', slug=conference.slug)
    else:
        form = ConferenceReviewForm()

    return render(request, 'conferences/add_review.html', {
        'conference': conference,
        'form': form
    })


class ConferenceByTopicView(ListView):
    """
    Конференции по определенной тематике
    """
    model = Conference
    template_name = 'conferences/conference_list.html'
    context_object_name = 'conferences'
    paginate_by = 10

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, slug=self.kwargs['topic_slug'])
        return Conference.objects.filter(
            status=Conference.Status.PUBLISHED,
            topics=self.topic
        ).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_topic'] = self.topic
        context['topics'] = Topic.objects.filter(is_active=True)
        context['current_filters'] = {'topic': self.topic.slug}
        return context


@login_required
def my_applications(request):
    """
    Список заявок текущего пользователя
    """
    applications = ConferenceApplication.objects.filter(
        user=request.user
    ).select_related('conference').order_by('-created_at')

    return render(request, 'conferences/my_applications.html', {
        'applications': applications
    })


@login_required
def cancel_application(request, pk):
    """
    Отмена заявки на участие
    """
    application = get_object_or_404(ConferenceApplication, pk=pk, user=request.user)

    if request.method == 'POST':
        if application.status in ['new', 'under_review']:
            conference = application.conference
            application.delete()

            # Уменьшаем счетчик заявок
            conference.applications_count -= 1
            conference.save(update_fields=['applications_count'])

            messages.success(request, 'Заявка отменена')
        else:
            messages.error(request, 'Нельзя отменить заявку на этом этапе')

    return redirect('conferences:my_applications')
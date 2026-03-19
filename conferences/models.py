# conferences/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import date
import uuid

from organizations.models import Organization
from django.conf import settings


class Topic(models.Model):
    """
    Тематика мероприятия (научное направление)
    """
    name = models.CharField(
        'Название тематики',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        'URL-идентификатор',
        unique=True,
        blank=True,
        help_text='Будет создан автоматически из названия'
    )
    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Краткое описание тематики'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская тематика',
        help_text='Для иерархии тематик (например: Физика -> Ядерная физика)'
    )
    is_active = models.BooleanField(
        'Активна',
        default=True,
        help_text='Отображать ли в фильтрах'
    )
    order = models.PositiveIntegerField(
        'Порядок сортировки',
        default=0,
        help_text='Меньше значение = выше в списке'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Тематика'
        verbose_name_plural = 'Тематики'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('conferences:by_topic', args=[self.slug])


class Conference(models.Model):
    """
    Модель научного мероприятия (конференция, форум, семинар, круглый стол)
    """

    # Статусы мероприятия
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        PENDING = 'pending', 'На модерации'
        PUBLISHED = 'published', 'Опубликовано'
        REJECTED = 'rejected', 'Отклонено'
        ARCHIVED = 'archived', 'В архиве'
        CANCELLED = 'cancelled', 'Отменено'

    # Типы мероприятий (расширенный список)
    class EventType(models.TextChoices):
        CONFERENCE = 'conference', 'Конференция'
        FORUM = 'forum', 'Форум'
        SEMINAR = 'seminar', 'Семинар'
        ROUND_TABLE = 'round_table', 'Круглый стол'
        SYMPOSIUM = 'symposium', 'Симпозиум'
        CONGRESS = 'congress', 'Конгресс'
        SCHOOL = 'school', 'Школа-конференция'
        WORKSHOP = 'workshop', 'Мастер-класс'

    # Форматы проведения
    class Format(models.TextChoices):
        OFFLINE = 'offline', 'Очная (офлайн)'
        ONLINE = 'online', 'Онлайн'
        HYBRID = 'hybrid', 'Гибридная (очно + онлайн)'

    # Форматы участия для заявок
    class ParticipationFormat(models.TextChoices):
        OFFLINE = 'offline', 'Очно'
        ONLINE = 'online', 'Дистанционно'
        HYBRID = 'hybrid', 'Гибридно (можно выбрать при подаче)'

    # Основная информация
    title = models.CharField(
        'Название мероприятия',
        max_length=300,
        help_text='Полное официальное название'
    )
    short_title = models.CharField(
        'Краткое название',
        max_length=100,
        blank=True,
        help_text='Аббревиатура или краткая форма (например: "ICM-2026")'
    )
    slug = models.SlugField(
        'URL-идентификатор',
        unique=True,
        blank=True,
        help_text='Будет создан автоматически из названия'
    )

    # Связи
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name='Организатор',
        related_name='conferences',
        help_text='Организация, проводящая мероприятие'
    )
    topics = models.ManyToManyField(
        Topic,
        verbose_name='Научные направления',
        related_name='conferences',
        help_text='Выберите тематики мероприятия (можно несколько)'
    )

    # Тип и формат
    event_type = models.CharField(
        'Тип мероприятия',
        max_length=20,
        choices=EventType.choices,
        default=EventType.CONFERENCE
    )
    format = models.CharField(
        'Формат проведения',
        max_length=20,
        choices=Format.choices,
        default=Format.OFFLINE
    )
    participation_format = models.CharField(
        'Доступные форматы участия',
        max_length=20,
        choices=ParticipationFormat.choices,
        default=ParticipationFormat.HYBRID,
        help_text='Выберите, какие форматы участия доступны'
    )

    # Даты
    start_date = models.DateField(
        'Дата начала',
        help_text='Дата начала мероприятия'
    )
    end_date = models.DateField(
        'Дата окончания',
        help_text='Дата окончания мероприятия'
    )
    deadline = models.DateField(
        'Дедлайн подачи заявок',
        help_text='Последний день подачи заявок/тезисов'
    )

    # Место проведения
    location = models.CharField(
        'Место проведения',
        max_length=255,
        blank=True,
        help_text='Город, место проведения (для онлайн - укажите "Онлайн")'
    )
    venue = models.CharField(
        'Площадка проведения',
        max_length=255,
        blank=True,
        help_text='Конкретное место: название вуза, конференц-зала и т.д.'
    )
    address = models.TextField(
        'Адрес проведения',
        blank=True,
        help_text='Полный адрес с индексом'
    )
    online_platform = models.CharField(
        'Платформа для онлайн-участия',
        max_length=200,
        blank=True,
        help_text='Например: Zoom, Webinar, Яндекс Телемост'
    )
    online_meeting_link = models.URLField(
        'Ссылка на онлайн-встречу',
        blank=True,
        help_text='Ссылка на Яндекс Телемост или другую платформу (будет отправлена участникам)'
    )

    # Детальное описание
    description = models.TextField(
        'Описание мероприятия',
        help_text='Подробное описание, цели, задачи'
    )
    program = models.TextField(
        'Программа мероприятия',
        blank=True,
        help_text='Программа мероприятия, пленарные докладчики'
    )
    requirements = models.TextField(
        'Требования к оформлению',
        blank=True,
        help_text='Требования к тезисам, статьям, презентациям'
    )
    requirements_link = models.URLField(
        'Ссылка на требования',
        blank=True,
        help_text='Ссылка на страницу с требованиями на вашем сайте'
    )
    requirements_file = models.FileField(
        'Файл с требованиями',
        upload_to='conferences/requirements/',
        blank=True,
        null=True,
        help_text='Загрузите файл с требованиями (PDF, DOC, DOCX)'
    )
    participation_terms = models.TextField(
        'Условия участия',
        blank=True,
        help_text='Организационный взнос, проживание, трансфер'
    )

    # Контакты
    contact_email = models.EmailField(
        'Контактный email',
        help_text='Email оргкомитета для вопросов'
    )
    contact_phone = models.CharField(
        'Контактный телефон',
        max_length=20,
        blank=True
    )
    contact_person = models.CharField(
        'Контактное лицо',
        max_length=200,
        blank=True,
        help_text='К кому обращаться по вопросам'
    )

    # Ссылки
    website = models.URLField(
        'Сайт мероприятия',
        blank=True,
        help_text='Официальный сайт, если есть отдельный'
    )
    call_for_papers = models.URLField(
        'Ссылка на сборник тезисов',
        blank=True,
        help_text='Ссылка на форму подачи заявок'
    )

    # Визуальные материалы
    poster = models.ImageField(
        'Постер мероприятия',
        upload_to='conferences/posters/',
        blank=True,
        null=True,
        help_text='Изображение для привлечения внимания'
    )

    # Дополнительные опции
    is_featured = models.BooleanField(
        'Рекомендуемое',
        default=False,
        help_text='Показывать на главной в блоке "Рекомендуемые"'
    )
    is_free = models.BooleanField(
        'Бесплатное',
        default=True,
        help_text='Участие бесплатное?'
    )
    has_publications = models.BooleanField(
        'Публикация материалов',
        default=True,
        help_text='Планируется ли публикация сборника трудов?'
    )
    publication_indexing = models.CharField(
        'Индексация публикаций',
        max_length=200,
        blank=True,
        help_text='Например: РИНЦ, Scopus, WoS'
    )

    # Статусы и мета-информация
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    view_count = models.PositiveIntegerField(
        'Просмотры',
        default=0,
        editable=False
    )
    favorites_count = models.PositiveIntegerField(
        'В избранном',
        default=0,
        editable=False,
        help_text='Сколько пользователей добавили в избранное'
    )
    applications_count = models.PositiveIntegerField(
        'Заявок подано',
        default=0,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        'Дата публикации',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-start_date', 'title']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['-start_date']),
            models.Index(fields=['deadline']),
            models.Index(fields=['event_type']),
            models.Index(fields=['format']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if len(base_slug) > 50:
                base_slug = base_slug[:50]
            year_slug = f"{base_slug}-{self.start_date.year}"
            self.slug = year_slug

            original_slug = self.slug
            counter = 1
            while Conference.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                if counter > 100:
                    self.slug = f"{original_slug}-{uuid.uuid4().hex[:8]}"
                    break

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('conferences:conference_detail', args=[self.slug])

    def is_upcoming(self):
        """Проверка, предстоит ли мероприятие"""
        return self.start_date >= date.today()

    def is_ongoing(self):
        """Идет ли мероприятие сейчас"""
        today = date.today()
        return self.start_date <= today <= self.end_date

    def is_past(self):
        """Прошло ли мероприятие"""
        return self.end_date < date.today()

    def days_until_deadline(self):
        """Дней до дедлайна"""
        delta = self.deadline - date.today()
        return delta.days

    def deadline_passed(self):
        """Прошел ли дедлайн"""
        return self.deadline < date.today()

    def get_event_type_display_ru(self):
        """Русское отображение типа мероприятия"""
        return dict(self.EventType.choices).get(self.event_type, '')


from django.contrib.auth import get_user_model

User = get_user_model()


class ConferenceApplication(models.Model):
    """
    Заявка на участие в мероприятии
    """

    class ApplicationStatus(models.TextChoices):
        NEW = 'new', 'Новая'
        UNDER_REVIEW = 'under_review', 'На рассмотрении'
        ACCEPTED = 'accepted', 'Принята'
        REJECTED = 'rejected', 'Отклонена'
        WAITLIST = 'waitlist', 'Лист ожидания'
        PAYMENT_PENDING = 'payment', 'Ожидает оплаты'
        CONFIRMED = 'confirmed', 'Подтверждена'
        CANCELLED = 'cancelled', 'Отменена'

    class ParticipationFormat(models.TextChoices):
        OFFLINE = 'offline', 'Очно'
        ONLINE = 'online', 'Дистанционно'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    # Информация об участнике
    full_name = models.CharField('ФИО', max_length=255)
    email = models.EmailField()
    organization = models.CharField('Место работы/учебы', max_length=255)
    position = models.CharField('Должность', max_length=200, blank=True)
    academic_degree = models.CharField('Ученая степень', max_length=100, blank=True)

    # Выбор формата участия
    participation_format = models.CharField(
        'Формат участия',
        max_length=20,
        choices=ParticipationFormat.choices,
        default=ParticipationFormat.OFFLINE,
        help_text='Выберите предпочтительный формат участия'
    )

    # Информация о докладе
    presentation_title = models.CharField('Тема доклада', max_length=500)
    presentation_type = models.CharField(
        'Тип доклада',
        max_length=50,
        choices=[
            ('plenary', 'Пленарный'),
            ('section', 'Секционный'),
            ('poster', 'Стендовый'),
            ('workshop', 'Мастер-класс'),
            ('listener', 'Слушатель (без доклада)'),
        ],
        default='section'
    )
    abstract = models.FileField(
        'Файл с тезисами',
        upload_to='applications/abstracts/',
        blank=True,
        null=True
    )
    abstract_text = models.TextField(
        'Текст тезисов',
        blank=True,
        help_text='Можно вставить текст тезисов, если нет файла'
    )

    # Комментарии
    comment = models.TextField(
        'Комментарий к заявке',
        blank=True,
        help_text='Дополнительная информация для оргкомитета'
    )

    # Статус заявки
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW
    )
    organizer_comment = models.TextField(
        'Комментарий организатора',
        blank=True,
        help_text='Внутренний комментарий оргкомитета'
    )

    # Ссылка на онлайн-встречу (заполняется при подтверждении)
    meeting_link = models.URLField(
        'Ссылка на онлайн-встречу',
        blank=True,
        help_text='Ссылка для дистанционных участников'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заявка на участие'
        verbose_name_plural = 'Заявки на участие'
        ordering = ['-created_at']
        unique_together = ['user', 'conference']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['conference', 'status']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.conference.title}"


class ConferenceReview(models.Model):
    """
    Отзыв на мероприятие
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.PositiveSmallIntegerField(
        'Оценка',
        choices=[(i, f'{i} звезд') for i in range(1, 6)]
    )
    title = models.CharField('Заголовок отзыва', max_length=200, blank=True)
    text = models.TextField('Текст отзыва')

    # Плюсы и минусы (опционально)
    pros = models.TextField('Что понравилось', blank=True)
    cons = models.TextField('Что можно улучшить', blank=True)

    is_verified = models.BooleanField(
        'Подтвержденный участник',
        default=False,
        help_text='Пользователь действительно участвовал в мероприятии'
    )
    is_published = models.BooleanField('Опубликован', default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'conference')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.conference.title} ({self.rating}★)"


class FavoriteConference(models.Model):
    """
    Избранные мероприятия пользователя
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_conferences'
    )
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'conference')
        verbose_name = 'Избранное мероприятие'
        verbose_name_plural = 'Избранные мероприятия'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.conference.title}"


class FavoriteOrganization(models.Model):
    """
    Избранные организации пользователя
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_organizations'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')
        verbose_name = 'Избранная организация'
        verbose_name_plural = 'Избранные организации'

    def __str__(self):
        return f"{self.user.email} - {self.organization.name}"


class ConferenceFile(models.Model):
    """
    Дополнительные файлы мероприятия (программа, информационное письмо и т.д.)
    """
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='files'
    )
    title = models.CharField('Название', max_length=200)
    file = models.FileField(
        'Файл',
        upload_to='conferences/files/'
    )
    file_type = models.CharField(
        'Тип файла',
        max_length=50,
        choices=[
            ('info_letter', 'Информационное письмо'),
            ('program', 'Программа'),
            ('rules', 'Правила оформления'),
            ('presentation', 'Презентация'),
            ('other', 'Другое'),
        ],
        default='info_letter'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Файл мероприятия'
        verbose_name_plural = 'Файлы мероприятия'

    def __str__(self):
        return self.title
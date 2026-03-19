# conferences/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import Topic, Conference, ConferenceApplication, ConferenceReview


class ConferenceApplicationInline(admin.TabularInline):
    model = ConferenceApplication
    extra = 0
    fields = ['full_name', 'email', 'presentation_title', 'status', 'participation_format']
    readonly_fields = ['full_name', 'email', 'presentation_title', 'participation_format']
    can_delete = False
    max_num = 0


class ConferenceReviewInline(admin.TabularInline):
    model = ConferenceReview
    extra = 0
    fields = ['user', 'rating', 'title', 'created_at']
    readonly_fields = ['user', 'rating', 'title', 'created_at']
    can_delete = False
    max_num = 0


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_active', 'conferences_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(conf_count=Count('conferences'))

    def conferences_count(self, obj):
        return obj.conf_count

    conferences_count.short_description = 'Мероприятий'


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'short_title', 'organization', 'event_type',  # Изменили conference_type на event_type
        'start_date', 'status', 'view_count', 'applications_count', 'is_featured'
    ]
    list_filter = [
        'status', 'event_type', 'format', 'is_featured', 'is_free',  # Изменили conference_type на event_type
        'organization', 'topics', 'start_date'
    ]
    search_fields = ['title', 'short_title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'view_count', 'favorites_count', 'applications_count',
        'created_at', 'updated_at', 'published_at', 'view_on_site_link'
    ]
    filter_horizontal = ['topics']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title', 'short_title', 'slug', 'organization', 'topics',
                ('event_type', 'format', 'participation_format'),  # Изменили
                ('status', 'is_featured', 'is_free'),
            )
        }),
        ('Даты', {
            'fields': (
                ('start_date', 'end_date', 'deadline'),
            )
        }),
        ('Место проведения', {
            'fields': (
                'location', 'venue', 'address', 'online_platform',
            )
        }),
        ('Описание и программа', {
            'fields': (
                'description', 'program', 'requirements', 'participation_terms',
                'requirements_link', 'requirements_file',  # Добавили новые поля
            )
        }),
        ('Контакты', {
            'fields': (
                'contact_email', 'contact_phone', 'contact_person',
            )
        }),
        ('Ссылки и медиа', {
            'fields': (
                'website', 'call_for_papers', 'poster', 'online_meeting_link',  # Добавили online_meeting_link
            )
        }),
        ('Публикации', {
            'fields': (
                'has_publications', 'publication_indexing',
            )
        }),
        ('Статистика', {
            'fields': (
                ('view_count', 'favorites_count', 'applications_count'),
                ('created_at', 'updated_at', 'published_at'),
                'view_on_site_link',
            )
        }),
    )

    inlines = [ConferenceApplicationInline, ConferenceReviewInline]

    actions = ['approve_conferences', 'reject_conferences', 'make_featured']

    def view_on_site_link(self, obj):
        if obj.pk and obj.status == 'published':
            url = reverse('conferences:conference_detail', args=[obj.slug])
            return format_html('<a href="{}" target="_blank">👁️ Просмотр на сайте</a>', url)
        return "-"

    view_on_site_link.short_description = 'Просмотр'

    def approve_conferences(self, request, queryset):
        queryset.update(status=Conference.Status.PUBLISHED, published_at=timezone.now())
        self.message_user(request, f"Одобрено {queryset.count()} мероприятий")

    approve_conferences.short_description = "Одобрить выбранные мероприятия"

    def reject_conferences(self, request, queryset):
        queryset.update(status=Conference.Status.REJECTED)
        self.message_user(request, f"Отклонено {queryset.count()} мероприятий")

    reject_conferences.short_description = "Отклонить выбранные мероприятия"

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"Помечено как рекомендуемое: {queryset.count()} мероприятий")

    make_featured.short_description = "Сделать рекомендуемыми"

    def save_model(self, request, obj, form, change):
        if obj.status == Conference.Status.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ConferenceApplication)
class ConferenceApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'conference', 'presentation_title',
        'participation_format', 'status', 'created_at', 'user_link'  # Добавили participation_format
    ]
    list_filter = ['status', 'presentation_type', 'participation_format', 'conference__organization']  # Добавили фильтр
    search_fields = ['full_name', 'email', 'presentation_title']
    readonly_fields = ['created_at', 'updated_at', 'user_link']

    fieldsets = (
        ('Информация об участнике', {
            'fields': (
                'full_name', 'email', 'organization', 'academic_degree',
                ('user', 'user_link'),
            )
        }),
        ('Информация о докладе и формате участия', {  # Изменили название
            'fields': (
                'presentation_title', 'presentation_type',
                'participation_format',  # Добавили поле
                'abstract', 'abstract_text',
            )
        }),
        ('Статус', {
            'fields': (
                'status', 'organizer_comment', 'meeting_link',  # Добавили meeting_link
                ('created_at', 'updated_at'),
            )
        }),
    )

    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_confirmed']

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_customuser_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return "-"

    user_link.short_description = 'Пользователь'

    def mark_as_accepted(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, f"Отмечено как принятые: {queryset.count()} заявок")

    mark_as_accepted.short_description = "Принять заявки"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"Отмечено как отклонённые: {queryset.count()} заявок")

    mark_as_rejected.short_description = "Отклонить заявки"

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"Отмечено как подтверждённые: {queryset.count()} заявок")

    mark_as_confirmed.short_description = "Подтвердить участие"


@admin.register(ConferenceReview)
class ConferenceReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'conference', 'rating', 'title', 'created_at', 'is_verified', 'is_published']
    list_filter = ['rating', 'is_verified', 'is_published', 'conference']
    search_fields = ['user__email', 'title', 'text']
    list_editable = ['is_published']

    actions = ['publish_reviews', 'unpublish_reviews']

    def publish_reviews(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано {queryset.count()} отзывов")

    publish_reviews.short_description = "Опубликовать отзывы"

    def unpublish_reviews(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f"Снято с публикации {queryset.count()} отзывов")

    unpublish_reviews.short_description = "Снять с публикации"
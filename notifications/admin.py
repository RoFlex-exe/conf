# notifications/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'notification_type', 'title', 'is_read',
        'is_emailed', 'created_at', 'conference_link'
    ]
    list_filter = ['notification_type', 'is_read', 'is_emailed', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at', 'read_at', 'conference_link', 'organization_link']

    fieldsets = (
        ('Информация', {
            'fields': (
                'user',
                ('notification_type', 'is_read', 'is_emailed'),
                'title',
                'message',
            )
        }),
        ('Связанные объекты', {
            'fields': (
                'conference_link',
                'organization_link',
            )
        }),
        ('Временные метки', {
            'fields': (
                ('created_at', 'read_at'),
            )
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread', 'resend_email']

    def conference_link(self, obj):
        if obj.conference:
            url = reverse('admin:conferences_conference_change', args=[obj.conference.id])
            return format_html('<a href="{}">{}</a>', url, obj.conference.title)
        return "-"

    conference_link.short_description = 'Конференция'

    def organization_link(self, obj):
        if obj.organization:
            url = reverse('admin:organizations_organization_change', args=[obj.organization.id])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return "-"

    organization_link.short_description = 'Организация'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"Отмечено как прочитанные: {queryset.count()}")

    mark_as_read.short_description = "Отметить как прочитанные"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"Отмечено как непрочитанные: {queryset.count()}")

    mark_as_unread.short_description = "Отметить как непрочитанные"

    def resend_email(self, request, queryset):
        # TODO: Переотправка email
        self.message_user(request, f"Запрошена переотправка для: {queryset.count()}")

    resend_email.short_description = "Переотправить на email"


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'notify_deadline', 'notify_application', 'notify_new_conference',
        'send_email', 'send_site', 'updated_at'
    ]
    list_filter = [
        'notify_deadline', 'notify_application', 'notify_new_conference',
        'send_email', 'send_site', 'send_weekly_digest'
    ]
    search_fields = ['user__email']

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Типы уведомлений', {
            'fields': (
                ('notify_deadline', 'notify_application'),
                ('notify_new_conference', 'notify_favorite_org'),
                ('notify_reminder',),
            )
        }),
        ('Доставка', {
            'fields': (
                ('send_email', 'send_site'),
                'send_weekly_digest',
            )
        }),
    )
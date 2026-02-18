# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'email', 'username', 'get_full_name', 'affiliation',
        'academic_degree', 'email_verified', 'is_active', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'email_verified', 'academic_degree',
        'date_joined', 'groups'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'affiliation']
    list_editable = ['email_verified']

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'middle_name',
                'affiliation',
                'academic_degree',
                'email_verified',
                'interests',
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'middle_name',
                'affiliation',
                'academic_degree',
            ),
        }),
    )

    filter_horizontal = ['interests', 'groups', 'user_permissions']

    actions = ['verify_emails', 'make_participants', 'send_welcome_email']

    def verify_emails(self, request, queryset):
        queryset.update(email_verified=True)
        self.message_user(request, f"Email подтверждён для {queryset.count()} пользователей")

    verify_emails.short_description = "Подтвердить email"

    def make_participants(self, request, queryset):
        # Снять статус организатора, если был
        queryset.update(organization=None)
        self.message_user(request, f"Пользователи переведены в статус участников: {queryset.count()}")

    make_participants.short_description = "Сделать участниками (не организаторами)"

    def send_welcome_email(self, request, queryset):
        # TODO: Отправка приветственного email
        self.message_user(request, f"Отправлены приветственные письма: {queryset.count()}")

    send_welcome_email.short_description = "Отправить приветственное письмо"
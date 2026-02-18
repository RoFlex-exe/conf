# organizations/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Organization, OrganizationDocument


class OrganizationDocumentInline(admin.TabularInline):
    model = OrganizationDocument
    extra = 1
    fields = ['title', 'file', 'document_type']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'short_name', 'inn', 'contact_person',
        'contact_email', 'is_active', 'is_verified', 'conferences_count'
    ]
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['name', 'short_name', 'inn', 'contact_email']
    list_editable = ['is_active', 'is_verified']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                ('name', 'short_name'),
                ('inn', 'kpp'),
                ('legal_address', 'actual_address'),
                ('established_date', 'website'),
                'logo',
                'description',
            )
        }),
        ('Контактная информация', {
            'fields': (
                ('contact_person', 'contact_position'),
                ('contact_email', 'contact_phone'),
                'contact_fax',
            )
        }),
        ('Статусы и связи', {
            'fields': (
                ('is_active', 'is_verified'),
                'user',
                ('created_at', 'updated_at'),
                'view_on_site_link',
            )
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'view_on_site_link']
    inlines = [OrganizationDocumentInline]

    actions = ['make_active', 'make_inactive', 'make_verified', 'send_credentials']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(conf_count=Count('conferences'))

    def conferences_count(self, obj):
        return obj.conf_count

    conferences_count.short_description = 'Конференций'

    def view_on_site_link(self, obj):
        if obj.pk:
            url = reverse('organizations:organization_detail', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">👁️ Просмотр на сайте</a>', url)
        return "-"

    view_on_site_link.short_description = 'Просмотр'

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} организаций")

    make_active.short_description = "Активировать выбранные организации"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {queryset.count()} организаций")

    make_inactive.short_description = "Деактивировать выбранные организации"

    def make_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"Верифицировано {queryset.count()} организаций")

    make_verified.short_description = "Подтвердить верификацию"

    def send_credentials(self, request, queryset):
        for org in queryset:
            # TODO: Отправка email с логином/паролем
            pass
        self.message_user(request, f"Отправлены данные для входа {queryset.count()} организациям")

    send_credentials.short_description = "Отправить данные для входа"
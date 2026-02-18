# organizations/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Organization(models.Model):
    """
    Модель организации (ВУЗ, НИИ, научный центр)
    """
    # Основная информация
    name = models.CharField(
        'Название организации',
        max_length=255,
        help_text='Полное официальное название'
    )
    short_name = models.CharField(
        'Краткое название',
        max_length=100,
        blank=True,
        help_text='Например: МГУ, НИЯУ МИФИ, ИППИ РАН'
    )
    inn = models.CharField(
        'ИНН',
        max_length=12,
        unique=True,
        help_text='Идентификационный номер налогоплательщика'
    )
    kpp = models.CharField(
        'КПП',
        max_length=9,
        blank=True,
        help_text='Код причины постановки на учет (для юрлиц)'
    )
    legal_address = models.TextField(
        'Юридический адрес',
        help_text='Официальный юридический адрес'
    )
    actual_address = models.TextField(
        'Фактический адрес',
        blank=True,
        help_text='Если отличается от юридического'
    )

    # Контактная информация
    contact_person = models.CharField(
        'Контактное лицо',
        max_length=255,
        help_text='ФИО ответственного за конференции'
    )
    contact_position = models.CharField(
        'Должность контактного лица',
        max_length=200,
        blank=True,
        help_text='Например: начальник отдела аспирантуры'
    )
    contact_email = models.EmailField(
        'Email для связи',
        help_text='На этот email будут приходить уведомления'
    )
    contact_phone = models.CharField(
        'Телефон',
        max_length=20,
        help_text='Контактный телефон с кодом города'
    )
    contact_fax = models.CharField(
        'Факс',
        max_length=20,
        blank=True
    )

    # Веб-присутствие
    website = models.URLField(
        'Сайт организации',
        blank=True,
        help_text='Официальный сайт'
    )
    logo = models.ImageField(
        'Логотип',
        upload_to='organizations/logos/',
        blank=True,
        null=True,
        help_text='Рекомендуемый размер: 200x200px'
    )

    # Дополнительная информация
    description = models.TextField(
        'Описание организации',
        blank=True,
        help_text='Краткая информация о деятельности, достижениях'
    )
    established_date = models.DateField(
        'Дата основания',
        null=True,
        blank=True
    )

    # Статусы и мета-информация
    is_active = models.BooleanField(
        'Договор активен',
        default=False,
        help_text='Организация может создавать конференции только при активном договоре'
    )
    is_verified = models.BooleanField(
        'Верифицирована',
        default=False,
        help_text='Официально подтверждено, что организация реальна'
    )
    created_at = models.DateTimeField(
        'Дата регистрации',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    # Связь с пользователем (представителем организации)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Представитель организации',
        related_name='organization',
        help_text='Аккаунт для входа в личный кабинет организации'
    )

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['name']
        indexes = [
            models.Index(fields=['inn']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.short_name or self.name

    def get_full_name(self):
        """Полное название с краткой формой в скобках"""
        if self.short_name and self.short_name != self.name:
            return f"{self.name} ({self.short_name})"
        return self.name

    def get_absolute_url(self):
        """URL страницы организации"""
        from django.urls import reverse
        return reverse('organization_detail', args=[str(self.id)])


class OrganizationDocument(models.Model):
    """
    Документы организации (договоры, скан-копии)
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField('Название документа', max_length=200)
    file = models.FileField(
        'Файл',
        upload_to='organizations/documents/'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(
        'Тип документа',
        max_length=50,
        choices=[
            ('contract', 'Договор'),
            ('certificate', 'Свидетельство'),
            ('other', 'Другое'),
        ],
        default='contract'
    )

    class Meta:
        verbose_name = 'Документ организации'
        verbose_name_plural = 'Документы организаций'

    def __str__(self):
        return f"{self.organization.name} - {self.title}"
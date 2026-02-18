# notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from conferences.models import Conference
from organizations.models import Organization

User = get_user_model()


class Notification(models.Model):
    """
    Модель уведомлений для пользователей
    """

    class NotificationType(models.TextChoices):
        DEADLINE = 'deadline', 'Приближение дедлайна'
        APPLICATION_STATUS = 'application', 'Изменение статуса заявки'
        NEW_CONFERENCE = 'new_conf', 'Новая конференция по интересам'
        FAVORITE_ORG = 'fav_org', 'Новости от избранной организации'
        REMINDER = 'reminder', 'Напоминание о конференции'
        SYSTEM = 'system', 'Системное уведомление'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    notification_type = models.CharField(
        'Тип уведомления',
        max_length=20,
        choices=NotificationType.choices
    )
    title = models.CharField('Заголовок', max_length=200)
    message = models.TextField('Текст уведомления')

    # Связанные объекты (опционально)
    conference = models.ForeignKey(
        Conference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Статусы
    is_read = models.BooleanField('Прочитано', default=False)
    is_emailed = models.BooleanField('Отправлено на email', default=False)

    # Мета-информация
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    read_at = models.DateTimeField('Прочитано', null=True, blank=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        """Отметить уведомление как прочитанное"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationSettings(models.Model):
    """
    Настройки уведомлений для пользователя
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        verbose_name='Пользователь'
    )

    # Типы уведомлений
    notify_deadline = models.BooleanField('Дедлайны', default=True)
    notify_application = models.BooleanField('Статус заявок', default=True)
    notify_new_conference = models.BooleanField('Новые конференции', default=True)
    notify_favorite_org = models.BooleanField('Новости от организаций', default=True)
    notify_reminder = models.BooleanField('Напоминания', default=True)

    # Периодичность
    send_weekly_digest = models.BooleanField('Еженедельный дайджест', default=False)

    # Способ доставки
    send_email = models.BooleanField('Отправлять на email', default=True)
    send_site = models.BooleanField('Показывать на сайте', default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Настройки уведомлений'
        verbose_name_plural = 'Настройки уведомлений'

    def __str__(self):
        return f"Настройки уведомлений: {self.user.email}"
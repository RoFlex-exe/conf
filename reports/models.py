# reports/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class Report(models.Model):
    """
    Модель для сохранённых отчётов
    """
    REPORT_TYPES = [
        ('conferences', 'Отчёт по конференциям'),
        ('applications', 'Отчёт по заявкам'),
        ('organizations', 'Отчёт по организациям'),
        ('users', 'Отчёт по пользователям'),
        ('custom', 'Пользовательский отчёт'),
    ]

    FORMAT_CHOICES = [
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]

    title = models.CharField('Название отчёта', max_length=200)
    report_type = models.CharField('Тип отчёта', max_length=20, choices=REPORT_TYPES)
    format = models.CharField('Формат', max_length=10, choices=FORMAT_CHOICES)

    # Параметры отчёта (хранятся в JSON)
    parameters = models.JSONField('Параметры', default=dict)

    # Результат
    file = models.FileField('Файл отчёта', upload_to='reports/', null=True, blank=True)

    # Статус
    STATUS_CHOICES = [
        ('pending', 'В очереди'),
        ('processing', 'Генерируется'),
        ('completed', 'Готов'),
        ('failed', 'Ошибка'),
    ]
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')

    # Владелец
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Ошибка если есть
    error_message = models.TextField('Сообщение об ошибке', blank=True)

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

    def mark_as_completed(self, file_path):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.file.name = file_path
        self.save()

    def mark_as_failed(self, error):
        self.status = 'failed'
        self.error_message = str(error)
        self.save()


class ScheduledReport(models.Model):
    """
    Запланированные отчёты
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('quarterly', 'Ежеквартально'),
    ]

    title = models.CharField('Название отчёта', max_length=200)
    report_type = models.CharField('Тип отчёта', max_length=20, choices=Report.REPORT_TYPES)
    format = models.CharField('Формат', max_length=10, choices=Report.FORMAT_CHOICES)
    parameters = models.JSONField('Параметры', default=dict)

    frequency = models.CharField('Периодичность', max_length=20, choices=FREQUENCY_CHOICES)
    recipients = models.TextField('Получатели', help_text='Email адреса через запятую')

    is_active = models.BooleanField('Активен', default=True)
    last_sent = models.DateTimeField('Последняя отправка', null=True, blank=True)
    next_run = models.DateTimeField('Следующий запуск')

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scheduled_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запланированный отчёт'
        verbose_name_plural = 'Запланированные отчёты'

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"
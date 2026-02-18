# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя - участника конференций
    """
    # Отчество
    middle_name = models.CharField(
        'Отчество',
        max_length=150,
        blank=True,
        help_text='Необязательное поле'
    )

    # Место работы/учебы - переименовали с organization на affiliation
    affiliation = models.CharField(
        'Место работы/учебы',
        max_length=255,
        blank=True,
        help_text='Например: МГУ им. Ломоносова, НИИ Ядерной физики, Школа №123 и т.д.'
    )

    # Ученая степень
    academic_degree = models.CharField(
        'Ученая степень',
        max_length=100,
        blank=True,
        choices=[
            ('', 'Нет степени'),
            ('student', 'Студент'),
            ('phd_student', 'Аспирант'),
            ('phd', 'Кандидат наук'),
            ('dsc', 'Доктор наук'),
            ('prof', 'Профессор'),
            ('assoc_prof', 'Доцент'),
            ('teacher', 'Преподаватель'),
            ('researcher', 'Научный сотрудник'),
            ('other', 'Другое'),
        ],
        help_text='Выберите ваш статус/степень'
    )

    # Подтверждение email
    email_verified = models.BooleanField(
        'Email подтвержден',
        default=False,
        help_text='Отметка о подтверждении email через письмо'
    )

    # Дата регистрации
    registered_at = models.DateTimeField(
        'Дата регистрации',
        auto_now_add=True
    )

    # Профессиональные интересы (для рекомендаций)
    interests = models.ManyToManyField(
        'conferences.Topic',
        verbose_name='Научные интересы',
        blank=True,
        help_text='Выберите тематики, которые вас интересуют'
    )

    def __str__(self):
        """Строковое представление пользователя"""
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
        return self.email or self.username

    def get_full_name(self):
        """Полное имя пользователя"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(part for part in parts if part)

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        ordering = ['-date_joined']
# reports/forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta


class ReportGenerateForm(forms.Form):
    """
    Форма для генерации отчётов
    """
    REPORT_TYPES = [
        ('conferences', 'По мероприятиям'),
        ('applications', 'По заявкам'),
        ('organizations', 'По организациям'),
        ('users', 'По пользователям'),
        ('statistics', 'Статистический'),
    ]

    FORMAT_CHOICES = [
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Тип отчёта'
    )
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Формат файла'
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название отчёта'}),
        label='Название отчёта',
        required=False
    )

    # Фильтры для конференций
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Дата с'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Дата по'
    )
    event_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + list(Conference.EventType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Тип мероприятия'
    )
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + list(Conference.Status.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Статус'
    )

    # Фильтры для заявок
    application_status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + list(ConferenceApplication.ApplicationStatus.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Статус заявки'
    )
    participation_format = forms.ChoiceField(
        choices=[('', 'Все форматы')] + list(ConferenceApplication.ParticipationFormat.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Формат участия'
    )

    # Фильтры для организаций
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Только активные'
    )
    is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Только верифицированные'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Импортируем модели здесь, чтобы избежать циклических импортов
        from conferences.models import Conference, ConferenceApplication

        # Устанавливаем начальные значения
        self.fields['date_to'].initial = timezone.now().date()
        self.fields['date_from'].initial = timezone.now().date() - timedelta(days=30)
        self.fields['title'].initial = f'Отчёт от {timezone.now().strftime("%d.%m.%Y")}'
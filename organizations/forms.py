# organizations/forms.py
from django import forms
from conferences.models import Conference, Topic, ConferenceApplication  # Добавили ConferenceApplication
from django.utils import timezone
from datetime import date


class ConferenceForm(forms.ModelForm):
    """
    Форма для создания и редактирования конференции
    """

    class Meta:
        model = Conference
        fields = [
            'title', 'short_title', 'conference_type', 'format',
            'start_date', 'end_date', 'deadline',
            'location', 'venue', 'address', 'online_platform',
            'description', 'program', 'requirements', 'participation_terms',
            'contact_email', 'contact_phone', 'contact_person',
            'website', 'call_for_papers',
            'poster', 'topics',
            'is_featured', 'is_free', 'has_publications', 'publication_indexing',
            'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Полное название конференции'}),
            'short_title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Краткое название (аббревиатура)'}),
            'conference_type': forms.Select(attrs={'class': 'form-select'}),
            'format': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город, страна'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название площадки'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Полный адрес'}),
            'online_platform': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Платформа для онлайн-участия'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Подробное описание конференции'}),
            'program': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Программа мероприятия'}),
            'requirements': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Требования к оформлению тезисов'}),
            'participation_terms': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Условия участия, оргвзнос'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО контактного лица'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'call_for_papers': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
            'topics': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
            'publication_indexing': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'РИНЦ, Scopus, WoS'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_publications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Название конференции *',
            'short_title': 'Краткое название',
            'conference_type': 'Тип конференции *',
            'format': 'Формат проведения *',
            'start_date': 'Дата начала *',
            'end_date': 'Дата окончания *',
            'deadline': 'Дедлайн подачи заявок *',
            'location': 'Место проведения *',
            'venue': 'Площадка проведения',
            'address': 'Адрес',
            'online_platform': 'Платформа для онлайн-участия',
            'description': 'Описание *',
            'program': 'Программа',
            'requirements': 'Требования к оформлению',
            'participation_terms': 'Условия участия',
            'contact_email': 'Контактный email *',
            'contact_phone': 'Контактный телефон',
            'contact_person': 'Контактное лицо',
            'website': 'Сайт конференции',
            'call_for_papers': 'Ссылка на сборник тезисов',
            'poster': 'Постер конференции',
            'topics': 'Научные направления *',
            'is_featured': 'Рекомендуемая (показывать на главной)',
            'is_free': 'Бесплатная',
            'has_publications': 'Публикация материалов',
            'publication_indexing': 'Индексация публикаций',
            'status': 'Статус',
        }
        help_texts = {
            'poster': 'Рекомендуемый размер: 1200x630px',
            'topics': 'Выберите одно или несколько направлений (Ctrl+Click для множественного выбора)',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        deadline = cleaned_data.get('deadline')

        # Проверка дат
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('Дата окончания не может быть раньше даты начала')

        if deadline and start_date:
            if deadline > start_date:
                raise forms.ValidationError('Дедлайн должен быть раньше даты начала конференции')

        return cleaned_data


class ConferenceApplicationStatusForm(forms.Form):
    """
    Форма для изменения статуса заявки
    """
    status = forms.ChoiceField(
        choices=ConferenceApplication.ApplicationStatus.choices,  # Теперь ConferenceApplication определён
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    organizer_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий для участника'})
    )
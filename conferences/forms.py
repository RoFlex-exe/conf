# conferences/forms.py
from django import forms
from .models import ConferenceApplication, ConferenceReview


class ConferenceApplicationForm(forms.ModelForm):
    """
    Форма для подачи заявки на участие в конференции
    """

    class Meta:
        model = ConferenceApplication
        fields = [
            'full_name',
            'email',
            'organization',
            'academic_degree',
            'presentation_title',
            'presentation_type',
            'abstract',
            'abstract_text',
            'comment',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivanov@example.com'
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'МГУ им. Ломоносова'
            }),
            'academic_degree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Кандидат наук / Студент / и т.д.'
            }),
            'presentation_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название доклада'
            }),
            'presentation_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'abstract': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'abstract_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Текст тезисов (если нет файла)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация для оргкомитета'
            }),
        }
        labels = {
            'full_name': 'ФИО *',
            'email': 'Email *',
            'organization': 'Место работы/учебы *',
            'academic_degree': 'Ученая степень/статус',
            'presentation_title': 'Тема доклада *',
            'presentation_type': 'Тип доклада *',
            'abstract': 'Файл с тезисами',
            'abstract_text': 'Текст тезисов',
            'comment': 'Комментарий',
        }
        help_texts = {
            'abstract': 'Принимаются файлы PDF, DOC, DOCX (максимум 5 МБ)',
            'abstract_text': 'Если у вас нет файла, вставьте текст тезисов сюда',
        }

    def clean(self):
        """
        Проверка, что хотя бы одно из полей (файл или текст) заполнено
        """
        cleaned_data = super().clean()
        abstract = cleaned_data.get('abstract')
        abstract_text = cleaned_data.get('abstract_text')

        if not abstract and not abstract_text:
            raise forms.ValidationError(
                'Загрузите файл с тезисами или вставьте текст тезисов'
            )

        return cleaned_data

    def clean_abstract(self):
        """
        Проверка размера файла
        """
        abstract = self.cleaned_data.get('abstract')
        if abstract:
            if abstract.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Размер файла не должен превышать 5 МБ')

            # Проверка расширения файла
            allowed_extensions = ['.pdf', '.doc', '.docx']
            ext = abstract.name.lower()
            if not any(ext.endswith(allowed) for allowed in allowed_extensions):
                raise forms.ValidationError('Разрешены только файлы PDF, DOC, DOCX')

        return abstract


class ConferenceReviewForm(forms.ModelForm):
    """
    Форма для отзыва на конференцию
    """

    class Meta:
        model = ConferenceReview
        fields = ['rating', 'title', 'text', 'pros', 'cons']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткий заголовок отзыва'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ваш отзыв о конференции'
            }),
            'pros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Что понравилось'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Что можно улучшить'
            }),
        }
        labels = {
            'rating': 'Оценка *',
            'title': 'Заголовок отзыва',
            'text': 'Текст отзыва *',
            'pros': 'Плюсы',
            'cons': 'Минусы',
        }
        help_texts = {
            'rating': 'Оцените конференцию от 1 до 5 звезд',
            'text': 'Поделитесь своими впечатлениями о конференции',
        }

    def clean_rating(self):
        """
        Проверка, что оценка в правильном диапазоне
        """
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Оценка должна быть от 1 до 5')
        return rating
# notifications/forms.py
from django import forms
from .models import NotificationSettings


class NotificationSettingsForm(forms.ModelForm):
    """
    Форма для настройки уведомлений пользователя
    """

    class Meta:
        model = NotificationSettings
        fields = [
            'notify_deadline',
            'notify_application',
            'notify_new_conference',
            'notify_favorite_org',
            'notify_reminder',
            'notify_invitation',
            'send_weekly_digest',
            'send_email',
            'send_site',
        ]
        widgets = {
            'notify_deadline': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_application': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_new_conference': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_favorite_org': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_reminder': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_invitation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_weekly_digest': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_site': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'notify_deadline': 'Уведомлять о дедлайнах',
            'notify_application': 'Уведомлять об изменении статуса заявок',
            'notify_new_conference': 'Уведомлять о новых мероприятиях по интересам',
            'notify_favorite_org': 'Уведомлять от избранных организаций',
            'notify_reminder': 'Напоминания о мероприятиях',
            'notify_invitation': 'Приглашения к участию',
            'send_weekly_digest': 'Еженедельный дайджест',
            'send_email': 'Отправлять на email',
            'send_site': 'Показывать на сайте',
        }
        help_texts = {
            'notify_deadline': 'Получать уведомления за 7, 3 и 1 день до дедлайна',
            'notify_application': 'При изменении статуса ваших заявок',
            'notify_new_conference': 'О новых мероприятиях по выбранным интересам',
            'notify_favorite_org': 'О новых мероприятиях от избранных организаций',
            'notify_reminder': 'Напоминания о начале мероприятий',
            'notify_invitation': 'Приглашения к участию от организаторов',
            'send_weekly_digest': 'Еженедельная подборка новых мероприятий',
            'send_email': 'Дублировать уведомления на email',
            'send_site': 'Показывать уведомления на сайте',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-check-input'
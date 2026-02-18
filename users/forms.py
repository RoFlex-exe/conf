# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    middle_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество (необязательно)'})
    )
    affiliation = forms.CharField(  # Переименовали с organization на affiliation
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Место работы/учебы'})
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'middle_name',
            'affiliation',  # Изменили здесь
            'academic_degree',
            'password1',
            'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы Bootstrap к стандартным полям
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Логин'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['academic_degree'].widget.attrs.update({'class': 'form-select'})


class CustomUserChangeForm(UserChangeForm):
    """
    Форма для редактирования профиля пользователя
    """
    password = None  # Убираем поле пароля из формы редактирования

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'affiliation',  # Изменили здесь
            'academic_degree',
            'interests'  # Добавили интересы
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['academic_degree'].widget.attrs.update({'class': 'form-select'})
        self.fields['interests'].widget.attrs.update({'class': 'form-select', 'multiple': True})


class CustomLoginForm(AuthenticationForm):
    """
    Кастомная форма входа с Bootstrap стилями
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите логин или email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
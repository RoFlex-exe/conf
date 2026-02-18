# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm

def register(request):
    """
    Регистрация нового пользователя
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Сразу логиним пользователя после регистрации
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """
    Просмотр и редактирование профиля пользователя
    """
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})


# users/views.py - обновленная функция favorites

@login_required
def favorites(request):
    """
    Страница с избранными конференциями и организациями
    """
    from django.core.paginator import Paginator

    # Получаем все избранные конференции (объекты FavoriteConference)
    favorite_conferences_objs = request.user.favorite_conferences.select_related(
        'conference', 'conference__organization'
    ).all()

    # Получаем все избранные организации (объекты FavoriteOrganization)
    favorite_organizations_objs = request.user.favorite_organizations.select_related(
        'organization'
    ).all()

    # Извлекаем сами конференции и организации
    conferences_list = [fc.conference for fc in favorite_conferences_objs]
    organizations_list = [fo.organization for fo in favorite_organizations_objs]

    # Текущая вкладка и страница
    tab = request.GET.get('tab', 'conferences')
    page = request.GET.get('page', 1)

    # Пагинация
    conferences_paginator = Paginator(conferences_list, 10)
    organizations_paginator = Paginator(organizations_list, 10)

    if tab == 'organizations':
        organizations = organizations_paginator.get_page(page)
        conferences = conferences_paginator.get_page(1)
    else:
        conferences = conferences_paginator.get_page(page)
        organizations = organizations_paginator.get_page(1)

    return render(request, 'users/favorites.html', {
        'favorite_conferences': conferences,
        'favorite_organizations': organizations,
        'current_tab': tab,
    })

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


@login_required
def notification_settings(request):
    """
    Настройки уведомлений пользователя
    """
    if request.method == 'POST':
        messages.success(request, 'Настройки уведомлений сохранены')
        return redirect('notification_settings')

    return render(request, 'users/notifications.html')
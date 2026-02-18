# reports/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect


# Временные заглушки для проверки
@staff_member_required
def report_list(request):
    """Временная заглушка для списка отчётов"""
    return render(request, 'reports/list.html', {'reports': []})


@staff_member_required
def generate_report(request):
    """Временная заглушка для генерации отчёта"""
    if request.method == 'POST':
        messages.success(request, 'Функция генерации отчётов находится в разработке')
        return redirect('reports:list')

    return render(request, 'reports/generate.html', {
        'status_choices': [
            ('published', 'Опубликовано'),
            ('pending', 'На модерации'),
            ('draft', 'Черновик'),
            ('archived', 'В архиве'),
        ]
    })


@staff_member_required
def download_report(request, pk):
    """Временная заглушка для скачивания"""
    messages.error(request, 'Функция скачивания отчётов находится в разработке')
    return redirect('reports:list')


@staff_member_required
def delete_report(request, pk):
    """Временная заглушка для удаления"""
    if request.method == 'POST':
        messages.success(request, f'Отчёт {pk} удалён (заглушка)')
    return redirect('reports:list')


@staff_member_required
def scheduled_reports(request):
    """Временная заглушка для запланированных отчётов"""
    return render(request, 'reports/scheduled.html', {'reports': []})


@staff_member_required
def create_scheduled_report(request):
    """Временная заглушка для создания запланированного отчёта"""
    if request.method == 'POST':
        messages.success(request, 'Запланированный отчёт создан (заглушка)')
        return redirect('reports:scheduled')

    return render(request, 'reports/schedule_form.html')


@staff_member_required
def toggle_scheduled_report(request, pk):
    """Временная заглушка для включения/отключения"""
    return redirect('reports:scheduled')


@staff_member_required
def delete_scheduled_report(request, pk):
    """Временная заглушка для удаления запланированного отчёта"""
    return redirect('reports:scheduled')
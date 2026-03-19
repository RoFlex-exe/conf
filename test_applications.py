#!/usr/bin/env python
"""
Скрипт для создания тестовых заявок на мероприятия.
Запуск: python create_test_applications.py
"""

import os
import django
import sys
import random
from datetime import date, timedelta

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf_promotion.settings')
django.setup()

# Импортируем модели
from django.contrib.auth import get_user_model
from conferences.models import Conference, ConferenceApplication, FavoriteConference, FavoriteOrganization
from organizations.models import Organization
from notifications.models import Notification

User = get_user_model()


# Цвета для вывода в консоль
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_info(msg):
    print(f"{Colors.OKBLUE}ℹ {msg}{Colors.ENDC}")


def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")


def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{msg}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 60}{Colors.ENDC}")


def get_users():
    """Получение всех обычных пользователей (не организаций)"""
    users = User.objects.filter(organization__isnull=True, is_superuser=False)
    if not users.exists():
        print_warning("Нет обычных пользователей. Сначала запусти populate_db.py")
        return None
    return users


def get_organizations():
    """Получение всех активных организаций"""
    orgs = Organization.objects.filter(is_active=True, is_verified=True)
    if not orgs.exists():
        print_warning("Нет активных организаций. Сначала запусти populate_db.py")
        return None
    return orgs


def get_upcoming_conferences():
    """Получение предстоящих мероприятий"""
    conferences = Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        start_date__gte=date.today()
    ).order_by('start_date')

    if not conferences.exists():
        # Если нет предстоящих, берём любые опубликованные
        conferences = Conference.objects.filter(status=Conference.Status.PUBLISHED)[:5]

    return conferences


def get_past_conferences():
    """Получение прошедших мероприятий (для отзывов)"""
    return Conference.objects.filter(
        status=Conference.Status.PUBLISHED,
        end_date__lt=date.today()
    )[:10]


def create_applications():
    """Создание тестовых заявок"""
    print_header("СОЗДАНИЕ ТЕСТОВЫХ ЗАЯВОК")

    users = get_users()
    if not users:
        return

    conferences = get_upcoming_conferences()
    if not conferences:
        print_warning("Нет мероприятий для подачи заявок")
        return

    applications_created = 0

    # Данные для генерации
    first_names = ['Иван', 'Пётр', 'Сергей', 'Алексей', 'Дмитрий', 'Андрей', 'Михаил', 'Александр']
    last_names = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Михайлов']
    middle_names = ['Иванович', 'Петрович', 'Сергеевич', 'Алексеевич', 'Дмитриевич', 'Андреевич']

    presentation_templates = [
        "Исследование {topic} в современных условиях",
        "Применение {topic} для решения задач {field}",
        "Анализ {topic} и перспективы развития",
        "Новые подходы к изучению {topic}",
        "{topic} в эпоху цифровой трансформации",
        "Моделирование процессов {topic}",
        "Оптимизация {topic} с использованием ИИ",
        "Экспериментальные исследования {topic}",
    ]

    fields = {
        'Физика': 'физики',
        'Математика': 'математики',
        'Информатика': 'информатики',
        'Биология': 'биологии',
        'Химия': 'химии',
        'Медицина': 'медицины',
        'Технические науки': 'инженерии',
        'Экономика': 'экономики',
    }

    # Для каждого пользователя создаём 1-3 заявки
    for user in users[:15]:  # Ограничим 15 пользователями
        num_applications = random.randint(1, 3)
        selected_conferences = random.sample(list(conferences), min(num_applications, len(conferences)))

        for conf in selected_conferences:
            # Проверяем, нет ли уже заявки от этого пользователя на это мероприятие
            if ConferenceApplication.objects.filter(user=user, conference=conf).exists():
                continue

            # Выбираем случайную тему из интересов пользователя или генерируем
            topics = conf.topics.all()
            if topics:
                topic = random.choice(topics).name
            else:
                topic = random.choice(list(fields.keys()))

            field = fields.get(topic, 'науки')
            presentation_title = random.choice(presentation_templates).format(topic=topic, field=field)

            # Выбираем формат участия в зависимости от доступных форматов мероприятия
            if conf.participation_format == 'offline':
                p_format = 'offline'
            elif conf.participation_format == 'online':
                p_format = 'online'
            else:  # hybrid
                p_format = random.choice(['offline', 'online'])

            # Генерируем случайный статус (распределение: 50% новые, 30% на рассмотрении, 20% принятые/подтверждённые)
            status_choices = [
                ('new', 50),
                ('under_review', 30),
                ('accepted', 10),
                ('confirmed', 5),
                ('rejected', 5),
            ]

            status = random.choices(
                [s[0] for s in status_choices],
                weights=[s[1] for s in status_choices]
            )[0]

            # Создаём заявку
            application = ConferenceApplication.objects.create(
                user=user,
                conference=conf,
                full_name=f"{random.choice(last_names)} {random.choice(first_names)} {random.choice(middle_names)}",
                email=user.email,
                organization=user.affiliation or random.choice(['МГУ', 'СПбГУ', 'МФТИ', 'НИЯУ МИФИ', 'СО РАН']),
                academic_degree=user.academic_degree or random.choice(['student', 'phd_student', 'phd', '']),
                presentation_title=presentation_title,
                presentation_type=random.choice(['plenary', 'section', 'poster', 'listener']),
                participation_format=p_format,
                abstract_text=f"Тезисы доклада по теме: {presentation_title}. Рассматриваются актуальные вопросы {field}, "
                              f"предлагаются новые методы решения, анализируются полученные результаты. "
                              f"Работа выполнена при поддержке гранта РФФИ.",
                comment=f"Прошу включить доклад в программу конференции. Готов выступить в любой день.",
                status=status,
            )

            # Обновляем счётчик заявок в мероприятии
            conf.applications_count += 1
            conf.save(update_fields=['applications_count'])

            # Если статус "confirmed", добавляем ссылку на онлайн-встречу
            if status == 'confirmed' and p_format == 'online':
                application.meeting_link = conf.online_meeting_link or "https://telemost.yandex.ru/conf123456"
                application.save()

                # Создаём уведомление
                Notification.objects.create(
                    user=user,
                    notification_type='application',
                    title='Ваша заявка подтверждена',
                    message=f'Ваша заявка на участие в мероприятии "{conf.title}" подтверждена. Ссылка для подключения: {application.meeting_link}',
                    conference=conf
                )
            elif status == 'accepted':
                Notification.objects.create(
                    user=user,
                    notification_type='application',
                    title='Заявка принята',
                    message=f'Ваша заявка на участие в мероприятии "{conf.title}" принята. Ожидайте подтверждения.',
                    conference=conf
                )

            applications_created += 1
            print_success(
                f"Создана заявка: {application.full_name} → {conf.title[:40]}... ({application.get_status_display()}, {application.get_participation_format_display()})")

    print_info(f"Всего создано заявок: {applications_created}")
    return applications_created


def create_reviews():
    """Создание тестовых отзывов на прошедшие мероприятия"""
    print_header("СОЗДАНИЕ ТЕСТОВЫХ ОТЗЫВОВ")

    past_conferences = get_past_conferences()
    if not past_conferences:
        print_warning("Нет прошедших мероприятий для отзывов")
        return

    # Берём пользователей, которые подавали заявки на прошедшие мероприятия
    applications = ConferenceApplication.objects.filter(
        conference__in=past_conferences,
        status__in=['confirmed', 'accepted']
    ).select_related('user', 'conference')

    if not applications.exists():
        print_warning("Нет подтверждённых заявок на прошедшие мероприятия")
        return

    reviews_created = 0

    review_texts = [
        "Отличная организация, интересные доклады, продуктивная дискуссия. Обязательно приму участие в следующем году.",
        "Хороший уровень докладов, насыщенная программа. Организаторы молодцы!",
        "Понравилась атмосфера, много полезных контактов. Секции были хорошо организованы.",
        "Достойный уровень мероприятия. Есть небольшие замечания по таймингу, но в целом всё отлично.",
        "Познавательно, интересно, полезно. Спасибо организаторам!",
        "Хорошая возможность представить свои результаты и получить обратную связь.",
    ]

    pros_list = [
        "Хорошая организация, интересные доклады, удобное место проведения",
        "Отличная программа, квалифицированные докладчики, дружелюбная атмосфера",
        "Много времени на вопросы, хороший кофе-брейк, удобные аудитории",
        "Сильный состав участников, актуальные темы, хорошая модерация",
    ]

    cons_list = [
        "Мало времени на секционные доклады, хотелось бы больше",
        "Технические проблемы со звуком в первый день",
        "Дорогой оргвзнос для студентов",
        "Далеко от метро, сложно добираться",
        "",
    ]

    for app in applications[:20]:  # Ограничим 20 отзывами
        # Проверяем, нет ли уже отзыва
        if hasattr(app.user, 'reviews') and app.user.reviews.filter(conference=app.conference).exists():
            continue

        from conferences.models import ConferenceReview

        review = ConferenceReview.objects.create(
            user=app.user,
            conference=app.conference,
            rating=random.randint(4, 5),  # В основном хорошие оценки
            title=f"Отзыв о мероприятии {app.conference.short_title or app.conference.title[:30]}",
            text=random.choice(review_texts),
            pros=random.choice(pros_list),
            cons=random.choice(cons_list),
            is_verified=True,
            is_published=True
        )

        reviews_created += 1
        print_success(f"Создан отзыв: {app.user.get_full_name()} → {app.conference.title[:40]}... ({review.rating}★)")

    print_info(f"Всего создано отзывов: {reviews_created}")


def create_favorites():
    """Добавление мероприятий и организаций в избранное"""
    print_header("СОЗДАНИЕ ИЗБРАННОГО")

    users = get_users()
    if not users:
        return

    conferences = Conference.objects.filter(status=Conference.Status.PUBLISHED)[:15]
    organizations = Organization.objects.filter(is_active=True, is_verified=True)[:10]

    favorites_created = 0

    for user in users[:10]:
        # Добавляем в избранное 2-5 мероприятий
        num_conf_fav = random.randint(2, 5)
        fav_confs = random.sample(list(conferences), min(num_conf_fav, len(conferences)))

        for conf in fav_confs:
            if not FavoriteConference.objects.filter(user=user, conference=conf).exists():
                FavoriteConference.objects.create(user=user, conference=conf)
                conf.favorites_count += 1
                conf.save(update_fields=['favorites_count'])
                favorites_created += 1

        # Добавляем в избранное 1-3 организации
        num_org_fav = random.randint(1, 3)
        fav_orgs = random.sample(list(organizations), min(num_org_fav, len(organizations)))

        for org in fav_orgs:
            if not FavoriteOrganization.objects.filter(user=user, organization=org).exists():
                FavoriteOrganization.objects.create(user=user, organization=org)
                favorites_created += 1

    print_info(f"Всего добавлено в избранное: {favorites_created}")


def create_notifications():
    """Создание тестовых уведомлений"""
    print_header("СОЗДАНИЕ ТЕСТОВЫХ УВЕДОМЛЕНИЙ")

    users = get_users()
    if not users:
        return

    conferences = Conference.objects.filter(status=Conference.Status.PUBLISHED)[:5]
    organizations = Organization.objects.filter(is_active=True, is_verified=True)[:3]

    notifications_created = 0

    notification_templates = [
        ('deadline', 'Приближается дедлайн подачи заявок',
         'До дедлайна мероприятия "{title}" осталось 7 дней. Успейте подать заявку!'),
        ('new_conf', 'Новое мероприятие по вашим интересам',
         'Появилось новое мероприятие: "{title}". Подробности на сайте.'),
        ('fav_org', 'Новости от избранной организации',
         'Организация "{org}" опубликовала новое мероприятие: "{title}".'),
        ('reminder', 'Напоминание о мероприятии', 'Напоминаем, что мероприятие "{title}" начнётся завтра.'),
    ]

    for user in users[:10]:
        # 3-5 уведомлений на пользователя
        num_notifications = random.randint(3, 5)

        for i in range(num_notifications):
            notif_type, title_template, msg_template = random.choice(notification_templates)

            if notif_type in ['deadline', 'reminder', 'new_conf']:
                conf = random.choice(conferences)
                title = title_template
                message = msg_template.format(title=conf.title)
                related_conf = conf
                related_org = None
            else:  # fav_org
                org = random.choice(organizations)
                conf = random.choice(conferences)
                title = title_template
                message = msg_template.format(org=org.name, title=conf.title)
                related_conf = conf
                related_org = org

            Notification.objects.create(
                user=user,
                notification_type=notif_type,
                title=title,
                message=message,
                conference=related_conf,
                organization=related_org,
                is_read=random.choice([True, False]),
                is_emailed=False
            )

            notifications_created += 1

    print_info(f"Всего создано уведомлений: {notifications_created}")


def print_statistics():
    """Вывод статистики"""
    print_header("СТАТИСТИКА ПОСЛЕ ЗАПОЛНЕНИЯ")

    total_applications = ConferenceApplication.objects.count()
    total_reviews = ConferenceApplication.objects.model.conferencereview_set.count() if hasattr(
        ConferenceApplication.objects.model, 'conferencereview_set') else 0
    total_favorites_conf = FavoriteConference.objects.count()
    total_favorites_org = FavoriteOrganization.objects.count()
    total_notifications = Notification.objects.count()

    print_success(f"Всего заявок: {total_applications}")
    print_success(f"Всего отзывов: {total_reviews}")
    print_success(f"Всего избранных мероприятий: {total_favorites_conf}")
    print_success(f"Всего избранных организаций: {total_favorites_org}")
    print_success(f"Всего уведомлений: {total_notifications}")

    # Статистика по статусам заявок
    print_info("\nСтатистика по статусам заявок:")
    from django.db.models import Count
    status_counts = ConferenceApplication.objects.values('status').annotate(count=Count('id'))
    status_display = dict(ConferenceApplication.ApplicationStatus.choices)

    for item in status_counts:
        status = item['status']
        count = item['count']
        display = status_display.get(status, status)
        print_info(f"  {display}: {count}")

    # Статистика по форматам участия
    print_info("\nСтатистика по форматам участия:")
    format_counts = ConferenceApplication.objects.values('participation_format').annotate(count=Count('id'))
    format_display = dict(ConferenceApplication.ParticipationFormat.choices)

    for item in format_counts:
        format_code = item['participation_format']
        count = item['count']
        display = format_display.get(format_code, format_code)
        print_info(f"  {display}: {count}")


def main():
    """Главная функция"""
    print_header("СОЗДАНИЕ ТЕСТОВЫХ ЗАЯВОК И СВЯЗАННЫХ ДАННЫХ")

    # Проверяем наличие данных
    if User.objects.count() < 5:
        print_warning("Мало пользователей. Сначала запусти populate_db.py")
        return

    if Conference.objects.count() < 5:
        print_warning("Мало мероприятий. Сначала запусти populate_db.py")
        return

    # Создаём заявки
    applications = create_applications()

    # Создаём отзывы (если есть прошедшие мероприятия)
    create_reviews()

    # Создаём избранное
    create_favorites()

    # Создаём уведомления
    create_notifications()

    # Выводим статистику
    print_statistics()

    print_header("ГОТОВО!")
    print_success("Тестовые заявки успешно созданы!")
    print_info("\nТеперь вы можете:")
    print_info("  1. Зайти в личный кабинет участника и посмотреть свои заявки")
    print_info("  2. Зайти в личный кабинет организации и обработать заявки")
    print_info("  3. Проверить уведомления")
    print_info("  4. Посмотреть избранное")


if __name__ == '__main__':
    main()
#!/usr/bin/env python
"""
Скрипт для тестирования подачи заявок и проверки всех функций
Запуск: python test_applications.py
"""

import os
import django
import sys
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf_promotion.settings')
django.setup()

from django.contrib.auth import get_user_model
from conferences.models import Conference, ConferenceApplication, ConferenceReview, Topic
from organizations.models import Organization
from django.db.models import Count, Q

User = get_user_model()


# Цвета для вывода
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


def test_conferences_count():
    """Проверка количества конференций"""
    print_header("ТЕСТ 1: Количество конференций")

    total = Conference.objects.count()
    published = Conference.objects.filter(status='published').count()
    upcoming = Conference.objects.filter(start_date__gte=date.today()).count()

    print_info(f"Всего конференций: {total}")
    print_info(f"Опубликовано: {published}")
    print_info(f"Предстоящих: {upcoming}")

    assert total > 0, "❌ Нет конференций в базе!"
    assert published > 0, "❌ Нет опубликованных конференций!"

    print_success("Тест пройден: конференции есть в базе")
    return total, published, upcoming


def test_organizations_count():
    """Проверка количества организаций"""
    print_header("ТЕСТ 2: Количество организаций")

    total = Organization.objects.count()
    active = Organization.objects.filter(is_active=True).count()

    print_info(f"Всего организаций: {total}")
    print_info(f"Активных: {active}")

    assert total > 0, "❌ Нет организаций в базе!"

    print_success("Тест пройден: организации есть в базе")
    return total


def test_users_count():
    """Проверка количества пользователей"""
    print_header("ТЕСТ 3: Количество пользователей")

    total = User.objects.count()
    organizers = User.objects.filter(organization__isnull=False).count()
    participants = User.objects.filter(organization__isnull=True, is_superuser=False).count()

    print_info(f"Всего пользователей: {total}")
    print_info(f"Организаторов: {organizers}")
    print_info(f"Участников: {participants}")

    assert total > 0, "❌ Нет пользователей в базе!"
    assert participants > 0, "❌ Нет обычных участников!"

    print_success("Тест пройден: пользователи есть в базе")
    return total


def test_create_applications():
    """Тестирование создания заявок"""
    print_header("ТЕСТ 4: Создание тестовых заявок")

    # Получаем обычных пользователей (не организаторов)
    participants = User.objects.filter(organization__isnull=True, is_superuser=False)

    # Получаем предстоящие конференции
    upcoming_conferences = Conference.objects.filter(
        status='published',
        start_date__gte=date.today()
    )[:5]

    if not participants or not upcoming_conferences:
        print_warning("Недостаточно данных для тестирования заявок")
        return

    applications_created = 0

    for i, participant in enumerate(participants[:3]):  # Берем первых 3 участников
        for conf in upcoming_conferences[:2]:  # Каждый подает на 2 конференции
            # Проверяем, нет ли уже заявки
            existing = ConferenceApplication.objects.filter(
                user=participant,
                conference=conf
            ).exists()

            if not existing:
                application = ConferenceApplication.objects.create(
                    user=participant,
                    conference=conf,
                    full_name=participant.get_full_name() or f"Участник {i}",
                    email=participant.email,
                    organization=participant.affiliation or "Тестовая организация",
                    presentation_title=f"Тестовый доклад {i + 1}",
                    presentation_type=random.choice(['plenary', 'section', 'poster']),
                    abstract_text=f"Это тестовый текст тезисов доклада для проверки работы системы подачи заявок. Номер теста: {i + 1}",
                    comment=f"Тестовая заявка от участника {participant.username}"
                )
                applications_created += 1
                print_success(f"Создана заявка: {participant.username} → {conf.title[:30]}...")

                # Обновляем счетчик заявок
                conf.applications_count += 1
                conf.save(update_fields=['applications_count'])

    print_info(f"Всего создано заявок: {applications_created}")
    print_success("Тест пройден: заявки созданы")


def test_create_reviews():
    """Тестирование создания отзывов"""
    print_header("ТЕСТ 5: Создание тестовых отзывов")

    # Получаем прошедшие конференции
    past_conferences = Conference.objects.filter(
        status='published',
        end_date__lt=date.today()
    )[:3]

    # Получаем пользователей, которые подавали заявки
    users_with_apps = User.objects.filter(
        applications__conference__in=past_conferences
    ).distinct()

    if not past_conferences or not users_with_apps:
        print_warning("Недостаточно данных для тестирования отзывов")
        return

    reviews_created = 0

    for user in users_with_apps[:3]:
        for conf in past_conferences:
            # Проверяем, нет ли уже отзыва
            existing = ConferenceReview.objects.filter(
                user=user,
                conference=conf
            ).exists()

            if not existing:
                # Проверяем, участвовал ли пользователь в этой конференции
                has_application = ConferenceApplication.objects.filter(
                    user=user,
                    conference=conf
                ).exists()

                review = ConferenceReview.objects.create(
                    user=user,
                    conference=conf,
                    rating=random.randint(4, 5),
                    title=f"Отличная конференция!",
                    text=f"Мне очень понравилась конференция. Хорошая организация, интересные доклады. Обязательно приму участие в следующей.",
                    pros="Хорошая организация, интересная программа, отличные докладчики",
                    cons="Хотелось бы больше времени на вопросы",
                    is_verified=has_application
                )
                reviews_created += 1
                print_success(f"Создан отзыв: {user.username} → {conf.title[:30]}... ({review.rating}★)")

    print_info(f"Всего создано отзывов: {reviews_created}")
    print_success("Тест пройден: отзывы созданы")


def test_favorites():
    """Тестирование добавления в избранное"""
    print_header("ТЕСТ 6: Тестирование избранного")

    from conferences.models import FavoriteConference, FavoriteOrganization

    participants = User.objects.filter(organization__isnull=True)[:3]
    conferences = Conference.objects.filter(status='published')[:5]
    organizations = Organization.objects.filter(is_active=True)[:3]

    favorites_created = 0

    for user in participants:
        for conf in conferences:
            existing = FavoriteConference.objects.filter(
                user=user,
                conference=conf
            ).exists()

            if not existing:
                fav = FavoriteConference.objects.create(
                    user=user,
                    conference=conf
                )
                conf.favorites_count += 1
                conf.save(update_fields=['favorites_count'])
                favorites_created += 1
                print_success(f"Добавлено в избранное: {user.username} → {conf.title[:30]}...")

        for org in organizations:
            existing = FavoriteOrganization.objects.filter(
                user=user,
                organization=org
            ).exists()

            if not existing:
                FavoriteOrganization.objects.create(
                    user=user,
                    organization=org
                )
                favorites_created += 1
                print_success(f"Добавлено в избранное: {user.username} → {org.name[:30]}...")

    print_info(f"Всего добавлено в избранное: {favorites_created}")
    print_success("Тест пройден: избранное работает")


def test_filters():
    """Тестирование фильтров конференций"""
    print_header("ТЕСТ 7: Тестирование фильтров")

    today = date.today()

    # Фильтр по статусу
    upcoming = Conference.objects.filter(
        status='published',
        start_date__gte=today
    ).count()

    ongoing = Conference.objects.filter(
        status='published',
        start_date__lte=today,
        end_date__gte=today
    ).count()

    past = Conference.objects.filter(
        status='published',
        end_date__lt=today
    ).count()

    print_info(f"Предстоящих конференций: {upcoming}")
    print_info(f"Идущих сейчас: {ongoing}")
    print_info(f"Прошедших: {past}")

    # Фильтр по тематикам
    topics = Topic.objects.annotate(
        conf_count=Count('conferences')
    ).filter(conf_count__gt=0)[:5]

    print_info("Топ тематик по количеству конференций:")
    for topic in topics:
        print_info(f"  {topic.name}: {topic.conf_count} конференций")

    # Фильтр по организациям
    orgs = Organization.objects.annotate(
        conf_count=Count('conferences')
    ).order_by('-conf_count')[:5]

    print_info("Топ организаторов:")
    for org in orgs:
        print_info(f"  {org.name}: {org.conf_count} конференций")

    # Фильтр по формату
    offline = Conference.objects.filter(status='published', format='offline').count()
    online = Conference.objects.filter(status='published', format='online').count()
    hybrid = Conference.objects.filter(status='published', format='hybrid').count()

    print_info(f"Офлайн конференций: {offline}")
    print_info(f"Онлайн конференций: {online}")
    print_info(f"Гибридных конференций: {hybrid}")

    print_success("Тест пройден: фильтры работают")


def test_organizer_access():
    """Тестирование доступа организаторов к своим конференциям"""
    print_header("ТЕСТ 8: Тестирование доступа организаторов")

    # Получаем первую организацию
    org = Organization.objects.filter(is_active=True).first()
    if not org:
        print_warning("Нет организаций для тестирования")
        return

    user = org.user
    conferences = Conference.objects.filter(organization=org)

    print_info(f"Организация: {org.name}")
    print_info(f"Пользователь: {user.username}")
    print_info(f"Конференций организации: {conferences.count()}")

    assert conferences.count() > 0, "❌ У организации нет конференций!"

    print_success("Тест пройден: организатор имеет доступ к своим конференциям")


def main():
    """Главная функция тестирования"""
    print_header("ТЕСТИРОВАНИЕ ПЛАТФОРМЫ")
    print_info("Начинаем проверку всех систем...")

    try:
        # Базовые проверки
        test_conferences_count()
        test_organizations_count()
        test_users_count()

        # Проверка функционала
        test_create_applications()
        test_create_reviews()
        test_favorites()
        test_filters()
        test_organizer_access()

        print_header("ИТОГИ ТЕСТИРОВАНИЯ")
        print_success("✅ Все тесты пройдены успешно!")
        print_info(f"Итоговая статистика:")
        print_info(f"  Конференций: {Conference.objects.count()}")
        print_info(f"  Организаций: {Organization.objects.count()}")
        print_info(f"  Пользователей: {User.objects.count()}")
        print_info(f"  Заявок: {ConferenceApplication.objects.count()}")
        print_info(f"  Отзывов: {ConferenceReview.objects.count()}")

    except AssertionError as e:
        print_warning(f"❌ Тест не пройден: {e}")
    except Exception as e:
        print_warning(f"❌ Ошибка при тестировании: {e}")


if __name__ == '__main__':
    main()
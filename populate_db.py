#!/usr/bin/env python
"""
Скрипт для заполнения базы данных актуальными тестовыми данными.
Основан на реальных научных мероприятиях 2026-2027 годов.
Запуск: python populate_db.py
"""

import os
import django
import sys
from datetime import date, timedelta
import random
import re

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf_promotion.settings')
django.setup()

# Импортируем модели
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from users.models import CustomUser
from organizations.models import Organization
from conferences.models import Topic, Conference

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


def create_topics():
    """Создание иерархии тематик конференций с английскими slug'ями"""
    print_header("СОЗДАНИЕ ТЕМАТИК")

    # Словарь для перевода русских названий в английские slug'и
    TOPIC_SLUGS = {
        # Физика и астрономия
        'Физика': 'physics',
        'Физика плазмы': 'plasma-physics',
        'Физика частиц': 'particle-physics',
        'Физика полупроводников': 'semiconductor-physics',
        'Квантовая физика': 'quantum-physics',
        'Физика низких температур': 'low-temperature-physics',
        'Физика высоких энергий': 'high-energy-physics',
        'Нелинейный анализ': 'nonlinear-analysis',
        'Экстремальные задачи': 'extreme-problems',
        'Синхротронное излучение': 'synchrotron-radiation',

        # Математика и информатика
        'Математика': 'mathematics',
        'Прикладная математика': 'applied-mathematics',
        'Информатика': 'computer-science',
        'Искусственный интеллект': 'artificial-intelligence',
        'Суперкомпьютерные технологии': 'supercomputing',
        'Цифровизация': 'digitalization',
        'Супервычисления': 'supercomputing-2026',
        'Математическое моделирование': 'mathematical-modeling',

        # Науки о Земле
        'Науки о Земле': 'earth-sciences',
        'Геология': 'geology',
        'Геофизика': 'geophysics',
        'География': 'geography',
        'Сейсмология': 'seismology',
        'Сейсмическая безопасность': 'seismic-safety',
        'Геология и минеральные ресурсы': 'geology-mineral-resources',
        'Энергетика': 'energy',
        'Возобновляемая энергетика': 'renewable-energy',

        # Биология и медицина
        'Биология': 'biology',
        'Молекулярная биология': 'molecular-biology',
        'Медицина': 'medicine',
        'Медицинская химия': 'medicinal-chemistry',
        'Микробиология': 'microbiology',

        # Химия и материаловедение
        'Химия': 'chemistry',
        'Материаловедение': 'materials-science',
        'Функциональные материалы': 'functional-materials',
        'Наноуглерод': 'nanocarbon',
        'Сегнетоэлектрики': 'ferroelectrics',

        # Технические науки
        'Технические науки': 'engineering',
        'Энергетика': 'energy',
        'Возобновляемая энергетика': 'renewable-energy',
        'Телекоммуникации': 'telecommunications',
        'Радиофотоника': 'radiophotonics',
        'Космонавтика': 'cosmonautics',
        'Авиация': 'aviation',
        'Навигационные системы': 'navigation-systems',
        'Управление летательными аппаратами': 'aircraft-control',

        # Гуманитарные науки
        'Гуманитарные науки': 'humanities',
        'Лингвистика': 'linguistics',
        'Образование': 'education',
        'Иностранные языки': 'foreign-languages',
        'Социально-гуманитарные науки': 'social-humanities',
        'Фронтирные территории': 'frontier-territories',

        # Экономика и финансы
        'Экономика': 'economics',
        'Финансы': 'finance',
        'Инвестиции': 'investments',
        'Устойчивое развитие': 'sustainable-development',
        'Энергетическая политика': 'energy-policy',
    }

    # Данные тематик с указанием родителей
    topics_data = [
        # Физика и астрономия
        {'name': 'Физика', 'order': 10},
        {'name': 'Физика плазмы', 'parent': 'Физика', 'order': 11},
        {'name': 'Физика частиц', 'parent': 'Физика', 'order': 12},
        {'name': 'Физика полупроводников', 'parent': 'Физика', 'order': 13},
        {'name': 'Квантовая физика', 'parent': 'Физика', 'order': 14},
        {'name': 'Физика низких температур', 'parent': 'Физика', 'order': 15},

        # Математика и информатика
        {'name': 'Математика', 'order': 20},
        {'name': 'Прикладная математика', 'parent': 'Математика', 'order': 21},
        {'name': 'Нелинейный анализ', 'parent': 'Математика', 'order': 22},
        {'name': 'Экстремальные задачи', 'parent': 'Математика', 'order': 23},
        {'name': 'Информатика', 'order': 30},
        {'name': 'Искусственный интеллект', 'parent': 'Информатика', 'order': 31},
        {'name': 'Суперкомпьютерные технологии', 'parent': 'Информатика', 'order': 32},
        {'name': 'Супервычисления', 'parent': 'Информатика', 'order': 33},
        {'name': 'Математическое моделирование', 'parent': 'Информатика', 'order': 34},
        {'name': 'Цифровизация', 'parent': 'Информатика', 'order': 35},

        # Науки о Земле
        {'name': 'Науки о Земле', 'order': 40},
        {'name': 'Геология', 'parent': 'Науки о Земле', 'order': 41},
        {'name': 'Геофизика', 'parent': 'Науки о Земле', 'order': 42},
        {'name': 'География', 'parent': 'Науки о Земле', 'order': 43},
        {'name': 'Сейсмология', 'parent': 'Науки о Земле', 'order': 44},
        {'name': 'Сейсмическая безопасность', 'parent': 'Науки о Земле', 'order': 45},
        {'name': 'Геология и минеральные ресурсы', 'parent': 'Науки о Земле', 'order': 46},

        # Биология и медицина
        {'name': 'Биология', 'order': 50},
        {'name': 'Молекулярная биология', 'parent': 'Биология', 'order': 51},
        {'name': 'Микробиология', 'parent': 'Биология', 'order': 52},
        {'name': 'Медицина', 'order': 60},
        {'name': 'Медицинская химия', 'parent': 'Медицина', 'order': 61},

        # Химия и материаловедение
        {'name': 'Химия', 'order': 70},
        {'name': 'Материаловедение', 'order': 80},
        {'name': 'Функциональные материалы', 'parent': 'Материаловедение', 'order': 81},
        {'name': 'Наноуглерод', 'parent': 'Материаловедение', 'order': 82},
        {'name': 'Сегнетоэлектрики', 'parent': 'Материаловедение', 'order': 83},

        # Технические науки
        {'name': 'Технические науки', 'order': 90},
        {'name': 'Энергетика', 'parent': 'Технические науки', 'order': 91},
        {'name': 'Возобновляемая энергетика', 'parent': 'Энергетика', 'order': 92},
        {'name': 'Энергетическая политика', 'parent': 'Энергетика', 'order': 93},
        {'name': 'Телекоммуникации', 'parent': 'Технические науки', 'order': 94},
        {'name': 'Радиофотоника', 'parent': 'Технические науки', 'order': 95},
        {'name': 'Космонавтика', 'order': 100},
        {'name': 'Авиация', 'order': 110},
        {'name': 'Навигационные системы', 'parent': 'Технические науки', 'order': 111},
        {'name': 'Управление летательными аппаратами', 'parent': 'Технические науки', 'order': 112},

        # Гуманитарные науки
        {'name': 'Гуманитарные науки', 'order': 120},
        {'name': 'Лингвистика', 'parent': 'Гуманитарные науки', 'order': 121},
        {'name': 'Образование', 'parent': 'Гуманитарные науки', 'order': 122},
        {'name': 'Иностранные языки', 'parent': 'Лингвистика', 'order': 123},
        {'name': 'Социально-гуманитарные науки', 'parent': 'Гуманитарные науки', 'order': 124},
        {'name': 'Фронтирные территории', 'parent': 'Гуманитарные науки', 'order': 125},

        # Экономика и финансы
        {'name': 'Экономика', 'order': 130},
        {'name': 'Финансы', 'parent': 'Экономика', 'order': 131},
        {'name': 'Инвестиции', 'parent': 'Экономика', 'order': 132},
        {'name': 'Устойчивое развитие', 'parent': 'Экономика', 'order': 133},
    ]

    # Сначала создадим все тематики без родителей
    topics_dict = {}
    for topic_data in topics_data:
        if 'parent' not in topic_data:
            topic_name = topic_data['name']
            slug = TOPIC_SLUGS.get(topic_name, slugify(topic_name))

            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                defaults={
                    'slug': slug,
                    'order': topic_data['order'],
                    'is_active': True
                }
            )

            if not created and topic.slug != slug:
                old_slug = topic.slug
                topic.slug = slug
                topic.save()
                print_warning(f"Обновлён slug для '{topic_name}': {old_slug} -> {slug}")

            topics_dict[topic_name] = topic
            if created:
                print_success(f"Создана тематика: {topic.name} (slug: {topic.slug})")
            else:
                print_info(f"Тематика уже существует: {topic.name} (slug: {topic.slug})")

    # Теперь создаем дочерние тематики
    for topic_data in topics_data:
        if 'parent' in topic_data:
            parent = topics_dict.get(topic_data['parent'])
            if parent:
                topic_name = topic_data['name']
                slug = TOPIC_SLUGS.get(topic_name, slugify(topic_name))

                topic, created = Topic.objects.get_or_create(
                    name=topic_name,
                    defaults={
                        'slug': slug,
                        'parent': parent,
                        'order': topic_data['order'],
                        'is_active': True
                    }
                )

                if not created and (topic.slug != slug or topic.parent != parent):
                    old_slug = topic.slug
                    topic.slug = slug
                    topic.parent = parent
                    topic.save()
                    print_warning(f"Обновлён slug для '{topic_name}': {old_slug} -> {slug}")

                topics_dict[topic_name] = topic
                if created:
                    print_success(f"Создана подтематика: {topic.name} (→ {parent.name}, slug: {topic.slug})")

    return topics_dict


def check_topic_slugs():
    """Проверка, что все slug'и тематик корректны"""
    print_header("ПРОВЕРКА SLUG'ЕЙ ТЕМАТИК")

    all_ok = True

    for topic in Topic.objects.all():
        if re.match(r'^[-a-zA-Z0-9_]+$', topic.slug):
            print(f"✅ {topic.name}: '{topic.slug}'")
        else:
            print(f"❌ {topic.name}: '{topic.slug}' - содержит недопустимые символы!")
            all_ok = False

    slugs = {}
    for topic in Topic.objects.all():
        if topic.slug in slugs:
            print(f"❌ Дубликат slug: '{topic.slug}' используется для '{topic.name}' и '{slugs[topic.slug]}'")
            all_ok = False
        else:
            slugs[topic.slug] = topic.name

    if all_ok:
        print_success("Все slug'и тематик корректны и уникальны!")
    else:
        print_warning("Обнаружены проблемы с slug'ями тематик")

    return all_ok


def create_organizations_and_users():
    """Создание организаций и соответствующих пользователей"""
    print_header("СОЗДАНИЕ ОРГАНИЗАЦИЙ")

    organizations_data = [
        # МГУ им. М.В. Ломоносова
        {
            'username': 'msu_org',
            'password': 'MsuOrg2024!',
            'user_data': {
                'email': 'conferences@msu.ru',
                'first_name': 'Алексей',
                'last_name': 'Иванов',
                'affiliation': 'МГУ им. М.В. Ломоносова',
            },
            'org_data': {
                'name': 'Московский государственный университет имени М.В. Ломоносова',
                'short_name': 'МГУ',
                'inn': '7729082090',
                'kpp': '772901001',
                'legal_address': '119991, г. Москва, Ленинские горы, д. 1',
                'contact_person': 'Иванов Алексей Петрович',
                'contact_position': 'Начальник отдела научных мероприятий',
                'contact_email': 'conferences@msu.ru',
                'contact_phone': '+7 (495) 939-10-00',
                'website': 'https://www.msu.ru',
                'description': 'МГУ имени М.В. Ломоносова — крупнейший классический университет Российской Федерации, один из центров отечественной науки и культуры.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # СПбГУ
        {
            'username': 'spbu_org',
            'password': 'SpbuOrg2024!',
            'user_data': {
                'email': 'science@spbu.ru',
                'first_name': 'Елена',
                'last_name': 'Петрова',
                'affiliation': 'СПбГУ',
            },
            'org_data': {
                'name': 'Санкт-Петербургский государственный университет',
                'short_name': 'СПбГУ',
                'inn': '7801002274',
                'kpp': '780101001',
                'legal_address': '199034, г. Санкт-Петербург, Университетская наб., д. 7-9',
                'contact_person': 'Петрова Елена Сергеевна',
                'contact_position': 'Начальник управления научных исследований',
                'contact_email': 'science@spbu.ru',
                'contact_phone': '+7 (812) 328-20-00',
                'website': 'https://spbu.ru',
                'description': 'СПбГУ — старейший университет России, основанный в 1724 году. Проводит широкий спектр научных мероприятий.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # МФТИ
        {
            'username': 'mipt_org',
            'password': 'MiptOrg2024!',
            'user_data': {
                'email': 'science@mipt.ru',
                'first_name': 'Дмитрий',
                'last_name': 'Сидоров',
                'affiliation': 'МФТИ',
            },
            'org_data': {
                'name': 'Московский физико-технический институт',
                'short_name': 'МФТИ',
                'inn': '5040002432',
                'kpp': '504001001',
                'legal_address': '141701, Московская обл., г. Долгопрудный, Институтский пер., д. 9',
                'contact_person': 'Сидоров Дмитрий Иванович',
                'contact_position': 'Проректор по научной работе',
                'contact_email': 'science@mipt.ru',
                'contact_phone': '+7 (495) 408-45-54',
                'website': 'https://mipt.ru',
                'description': 'МФТИ — ведущий технический вуз России, готовящий специалистов в области теоретической и экспериментальной физики, математики и информатики.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # НИЯУ МИФИ
        {
            'username': 'mephi_org',
            'password': 'MephiOrg2024!',
            'user_data': {
                'email': 'science@mephi.ru',
                'first_name': 'Андрей',
                'last_name': 'Козлов',
                'affiliation': 'НИЯУ МИФИ',
            },
            'org_data': {
                'name': 'Национальный исследовательский ядерный университет «МИФИ»',
                'short_name': 'НИЯУ МИФИ',
                'inn': '7724068140',
                'kpp': '772401001',
                'legal_address': '115409, г. Москва, Каширское шоссе, д. 31',
                'contact_person': 'Козлов Андрей Николаевич',
                'contact_position': 'Начальник отдела организации научных мероприятий',
                'contact_email': 'science.conf@mephi.ru',
                'contact_phone': '+7 (495) 788-56-99',
                'website': 'https://mephi.ru',
                'description': 'НИЯУ МИФИ — один из ведущих технических университетов России, специализирующийся на ядерной физике, информационных технологиях и материаловедении.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # ФТИ им. А.Ф. Иоффе
        {
            'username': 'ioffe_org',
            'password': 'IoffeOrg2024!',
            'user_data': {
                'email': 'conferences@mail.ioffe.ru',
                'first_name': 'Сергей',
                'last_name': 'Лебедев',
                'affiliation': 'ФТИ им. А.Ф. Иоффе',
            },
            'org_data': {
                'name': 'Физико-технический институт им. А.Ф. Иоффе РАН',
                'short_name': 'ФТИ им. Иоффе',
                'inn': '7802012345',
                'kpp': '780201001',
                'legal_address': '194021, г. Санкт-Петербург, Политехническая ул., д. 26',
                'contact_person': 'Лебедев Сергей Германович',
                'contact_position': 'Учёный секретарь',
                'contact_email': 'conferences@mail.ioffe.ru',
                'contact_phone': '+7 (812) 297-22-45',
                'website': 'https://www.ioffe.ru',
                'description': 'ФТИ им. А.Ф. Иоффе — один из крупнейших научно-исследовательских институтов России в области физики.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # ОИВТ РАН (Объединенный институт высоких температур)
        {
            'username': 'jiht_org',
            'password': 'JihtOrg2024!',
            'user_data': {
                'email': 'conferences@jiht.ru',
                'first_name': 'Владимир',
                'last_name': 'Петров',
                'affiliation': 'ОИВТ РАН',
            },
            'org_data': {
                'name': 'Объединенный институт высоких температур РАН',
                'short_name': 'ОИВТ РАН',
                'inn': '7728012345',
                'kpp': '772801001',
                'legal_address': '125412, г. Москва, ул. Ижорская, д. 13, стр. 2',
                'contact_person': 'Петров Владимир Сергеевич',
                'contact_position': 'Учёный секретарь',
                'contact_email': 'conferences@jiht.ru',
                'contact_phone': '+7 (495) 484-23-33',
                'website': 'https://www.jiht.ru',
                'description': 'ОИВТ РАН проводит фундаментальные и прикладные исследования в области физики плазмы, энергетики, теплофизики.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # НИУ ВШЭ
        {
            'username': 'hse_org',
            'password': 'HseOrg2024!',
            'user_data': {
                'email': 'science@hse.ru',
                'first_name': 'Ярослав',
                'last_name': 'Кузьминов',
                'affiliation': 'НИУ ВШЭ',
            },
            'org_data': {
                'name': 'Национальный исследовательский университет «Высшая школа экономики»',
                'short_name': 'НИУ ВШЭ',
                'inn': '7710123456',
                'kpp': '771001001',
                'legal_address': '101000, г. Москва, ул. Мясницкая, д. 20',
                'contact_person': 'Кузьминов Ярослав Иванович',
                'contact_position': 'Ректор',
                'contact_email': 'science@hse.ru',
                'contact_phone': '+7 (495) 771-32-32',
                'website': 'https://www.hse.ru',
                'description': 'НИУ ВШЭ — ведущий исследовательский университет России. Проводит конференции по суперкомпьютерным технологиям, лингвистике, образованию и многим другим направлениям.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # МГТУ им. Баумана
        {
            'username': 'bmstu_org',
            'password': 'Bmstu2026!',
            'user_data': {
                'email': 'science@bmstu.ru',
                'first_name': 'Михаил',
                'last_name': 'Гордин',
                'affiliation': 'МГТУ им. Баумана',
            },
            'org_data': {
                'name': 'Московский государственный технический университет имени Н.Э. Баумана',
                'short_name': 'МГТУ им. Баумана',
                'inn': '7701012346',
                'kpp': '770101001',
                'legal_address': '105005, г. Москва, ул. 2-я Бауманская, д. 5, стр. 1',
                'contact_person': 'Гордин Михаил Валерьевич',
                'contact_position': 'Ректор',
                'contact_email': 'science@bmstu.ru',
                'contact_phone': '+7 (499) 263-65-05',
                'website': 'https://bmstu.ru',
                'description': 'МГТУ им. Н.Э. Баумана – ведущий технический университет России. Главный организатор Всероссийского форума «Шаг в будущее».',
                'is_active': True,
                'is_verified': True,
            }
        },
        # СО РАН (Сибирское отделение РАН)
        {
            'username': 'sbras_org',
            'password': 'Sbras2026!',
            'user_data': {
                'email': 'conferences@sbras.ru',
                'first_name': 'Валентин',
                'last_name': 'Пармон',
                'affiliation': 'СО РАН',
            },
            'org_data': {
                'name': 'Сибирское отделение Российской академии наук',
                'short_name': 'СО РАН',
                'inn': '5408001234',
                'kpp': '540801001',
                'legal_address': '630090, г. Новосибирск, проспект Академика Лаврентьева, 17',
                'contact_person': 'Пармон Валентин Николаевич',
                'contact_position': 'Председатель СО РАН',
                'contact_email': 'conferences@sbras.ru',
                'contact_phone': '+7 (383) 330-75-01',
                'website': 'https://www.sbras.ru',
                'description': 'Сибирское отделение РАН объединяет более 80 научных институтов. Проводит множество конференций по различным направлениям науки.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # ИЗК СО РАН (Институт земной коры)
        {
            'username': 'crust_org',
            'password': 'Crust2026!',
            'user_data': {
                'email': 'conferences@crust.irk.ru',
                'first_name': 'Дмитрий',
                'last_name': 'Гладкочуб',
                'affiliation': 'ИЗК СО РАН',
            },
            'org_data': {
                'name': 'Институт земной коры СО РАН',
                'short_name': 'ИЗК СО РАН',
                'inn': '3811001234',
                'kpp': '381101001',
                'legal_address': '664033, г. Иркутск, ул. Лермонтова, д. 128',
                'contact_person': 'Гладкочуб Дмитрий Петрович',
                'contact_position': 'Директор',
                'contact_email': 'conferences@crust.irk.ru',
                'contact_phone': '+7 (3952) 42-27-00',
                'website': 'https://www.crust.irk.ru',
                'description': 'Институт земной коры СО РАН проводит конференции по сейсмологии, геологии и сейсмической безопасности.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # АЛТГУ (Алтайский государственный университет)
        {
            'username': 'asu_org',
            'password': 'Asu2026!',
            'user_data': {
                'email': 'science@asu.ru',
                'first_name': 'Сергей',
                'last_name': 'Бочаров',
                'affiliation': 'АлтГУ',
            },
            'org_data': {
                'name': 'Алтайский государственный университет',
                'short_name': 'АлтГУ',
                'inn': '2225001234',
                'kpp': '222501001',
                'legal_address': '656049, г. Барнаул, проспект Ленина, д. 61',
                'contact_person': 'Бочаров Сергей Николаевич',
                'contact_position': 'Проректор по научной работе',
                'contact_email': 'science@asu.ru',
                'contact_phone': '+7 (3852) 29-12-58',
                'website': 'https://www.asu.ru',
                'description': 'Алтайский государственный университет проводит конференции по гуманитарным наукам, включая круглый стол по фронтирным территориям.',
                'is_active': True,
                'is_verified': True,
            }
        },
    ]

    organizations = {}

    for org_info in organizations_data:
        username = org_info['username']
        password = org_info['password']
        user_data = org_info['user_data']

        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults=user_data
        )

        if created:
            user.set_password(password)
            user.save()
            print_success(f"Создан пользователь: {username} ({user_data['email']})")
        else:
            print_info(f"Пользователь уже существует: {username}")

        org, created = Organization.objects.get_or_create(
            inn=org_info['org_data']['inn'],
            defaults={
                **org_info['org_data'],
                'user': user
            }
        )

        if created:
            print_success(f"Создана организация: {org.name}")
        else:
            print_info(f"Организация уже существует: {org.name}")

        organizations[org.short_name] = org

    return organizations


def create_conferences(organizations, topics):
    """Создание конференций на основе актуальных данных 2026-2027 годов"""
    print_header("СОЗДАНИЕ КОНФЕРЕНЦИЙ И МЕРОПРИЯТИЙ")

    today = date.today()

    # Актуальные мероприятия на основе поисковых результатов [citation:1][citation:2][citation:3]
    conferences_data = [
        # ОИВТ РАН - Возобновляемая энергетика (форум) [citation:1]
        {
            'title': 'VII Международная конференция «Возобновляемая энергетика: проблемы и перспективы»',
            'short_title': 'ВЭ-2026',
            'organization': organizations['ОИВТ РАН'],
            'event_type': 'forum',
            'format': 'offline',
            'participation_format': 'hybrid',
            'start_date': date(2026, 9, 21),
            'end_date': date(2026, 9, 24),
            'deadline': date(2026, 6, 1),
            'location': 'Махачкала',
            'venue': 'Дагестанский государственный университет',
            'address': 'г. Махачкала, ул. Гаджиева, 43-а',
            'description': 'VII Международная конференция «Возобновляемая энергетика: проблемы и перспективы» и XIII Школа молодых ученых «Актуальные проблемы освоения возобновляемых энергоресурсов» им. Э. Э. Шпильрайна. Мероприятие посвящено актуальным проблемам и перспективам развития возобновляемой энергетики в России и мире.',
            'program': 'Пленарные доклады, секционные заседания, школа молодых ученых, круглые столы.',
            'requirements': 'Требования к оформлению тезисов на сайте конференции.',
            'requirements_link': 'http://renen-conf.ru/requirements',
            'participation_terms': 'Организационный взнос: 6000 руб., для студентов и аспирантов - 3000 руб. Регистрация до 1 июня 2026 г.',
            'contact_email': 'renen@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'contact_person': 'Оргкомитет',
            'website': 'http://renen-conf.ru',
            'is_featured': True,
            'is_free': False,
            'has_publications': True,
            'publication_indexing': 'РИНЦ',
            'topics': ['Возобновляемая энергетика', 'Энергетика', 'Технические науки'],
        },

        # ОИВТ РАН - Физика низкотемпературной плазмы [citation:9]
        {
            'title': 'Всероссийская (с международным участием) конференция «Физика низкотемпературной плазмы»',
            'short_title': 'ФНТП-2026',
            'organization': organizations['ОИВТ РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 6, 1),
            'end_date': date(2026, 6, 5),
            'deadline': date(2026, 4, 20),
            'location': 'Казань',
            'venue': 'Казанский федеральный университет',
            'address': 'г. Казань, ул. Кремлевская, д. 18',
            'description': 'Всероссийская (с международным участием) конференция «Физика низкотемпературной плазмы» (ФНТП-2026). Конференция посвящена фундаментальным и прикладным аспектам физики низкотемпературной плазмы, плазменным технологиям и диагностике плазмы.',
            'program': 'Пленарные и секционные доклады, постерная сессия.',
            'requirements': 'Требования к оформлению на сайте конференции.',
            'requirements_link': 'https://jiht.ru/fntp2026',
            'participation_terms': 'Прием заявок до 20 апреля 2026 г.',
            'contact_email': 'plasma@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'website': 'https://jiht.ru/fntp2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Физика плазмы', 'Физика', 'Технические науки'],
        },

        # ОИВТ РАН - Молекулярная динамика [citation:9]
        {
            'title': 'II Всероссийская конференция «Молекулярная Динамика»',
            'short_title': 'MD-2026',
            'organization': organizations['ОИВТ РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 6, 28),
            'end_date': date(2026, 7, 5),
            'deadline': date(2026, 3, 1),
            'location': 'Санкт-Петербург, г. Пушкин',
            'venue': 'Конференц-центр',
            'address': 'г. Пушкин, Санкт-Петербург',
            'description': 'II Всероссийская конференция «Молекулярная Динамика» в г. Пушкин (Санкт-Петербург). Обсуждение современных методов молекулярного моделирования и их применений в различных областях науки.',
            'program': 'Пленарные лекции, секционные доклады, школы для молодых учёных.',
            'requirements': 'Окончание регистрации и приёма тезисов докладов до 1 марта 2026 г.',
            'requirements_link': 'https://jiht.ru/md2026',
            'participation_terms': 'Оргвзнос: 5000 руб. Для студентов и аспирантов: 2500 руб.',
            'contact_email': 'md@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'website': 'https://jiht.ru/md2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Физика', 'Химия', 'Биология', 'Молекулярная биология'],
        },

        # ОИВТ РАН - Звенигородская конференция по физике плазмы [citation:9]
        {
            'title': '53 МЕЖДУНАРОДНАЯ КОНФЕРЕНЦИЯ ПО ФИЗИКЕ ПЛАЗМЫ И УПРАВЛЯЕМОМУ ТЕРМОЯДЕРНОМУ СИНТЕЗУ',
            'short_title': 'Звенигород-2026',
            'organization': organizations['ОИВТ РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 3, 16),
            'end_date': date(2026, 3, 20),
            'deadline': date(2025, 11, 10),
            'location': 'Московская обл., Звенигород',
            'venue': 'Пансионат',
            'address': 'г. Звенигород, Московская обл.',
            'description': 'Крупнейшая конференция по физике плазмы и управляемому термоядерному синтезу, традиционно проводимая в Звенигороде. Ведущие учёные и специалисты представляют последние достижения в области физики плазмы, УТС и смежных направлениях.',
            'program': 'Пленарные и секционные доклады, постерная сессия. Основные направления: физика высокотемпературной плазмы, УТС, физические аспекты термоядерных реакторов.',
            'requirements': 'Докладчики должны были заполнить регистрационную форму до 10 ноября 2025 г.',
            'requirements_link': 'https://plasma2026.jiht.ru',
            'participation_terms': 'Оргвзнос: 8000 руб., для студентов 4000 руб.',
            'contact_email': 'plasma@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'website': 'https://plasma2026.jiht.ru',
            'is_featured': True,
            'is_free': False,
            'topics': ['Физика плазмы', 'Физика', 'Энергетика'],
        },

        # МГТУ им. Баумана - Шаг в будущее (форум) [citation:2]
        {
            'title': 'Всероссийский форум научной молодёжи «Шаг в будущее» 2026',
            'short_title': 'Шаг в будущее-2026',
            'organization': organizations['МГТУ им. Баумана'],
            'event_type': 'forum',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 3, 23),
            'end_date': date(2026, 3, 27),
            'deadline': date(2026, 1, 15),
            'location': 'Москва',
            'venue': 'МГТУ им. Баумана и другие площадки',
            'address': 'г. Москва',
            'description': 'Крупнейшее мероприятие Десятилетия науки и технологий для молодых исследователей и школьников, объединяющее 52 научные секции по всем направлениям: от инженерных наук до социально-гуманитарных. Организаторы: МГТУ им. Баумана, Российское молодёжное политехническое общество, при участии ведущих институтов РАН, госкорпораций и высокотехнологичных компаний. Председатель Программного комитета форума – Вице-президент РАН академик С.Н. Калмыков.',
            'program': '52 секции по 4 симпозиумам: Инженерные науки, Естественные науки, Математика и ИТ, Социально-гуманитарные науки. Научно-технологическая выставка, фестиваль молодых модельеров, битва команд за Научно-технологический кубок России. Участники: школьники, студенты колледжей и начальных курсов вузов.',
            'requirements': 'Подробные требования к работам на сайте форума.',
            'requirements_link': 'https://шагвбудущее.рф',
            'participation_terms': 'Участие бесплатное. Победители и призёры пользуются льготами при поступлении в вузы.',
            'contact_email': 'info@step-into-the-future.ru',
            'contact_phone': '+7 (499) 263-65-05',
            'website': 'https://шагвбудущее.рф',
            'is_featured': True,
            'is_free': True,
            'topics': [
                'Технические науки', 'Физика', 'Химия', 'Биология',
                'Математика', 'Информатика', 'Гуманитарные науки',
                'Экономика', 'Образование'
            ],
        },

        # ИПУ РАН - Нелинейный анализ и экстремальные задачи (школа-семинар) [citation:3]
        {
            'title': 'IX Международная школа-семинар «Нелинейный анализ и экстремальные задачи»',
            'short_title': 'NLA-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'school',
            'format': 'offline',
            'participation_format': 'hybrid',
            'start_date': date(2026, 6, 22),
            'end_date': date(2026, 6, 26),
            'deadline': date(2026, 5, 1),
            'location': 'Иркутск',
            'venue': 'Иркутский научный центр СО РАН',
            'address': 'г. Иркутск',
            'description': 'IX Международная школа-семинар «Нелинейный анализ и экстремальные задачи» (NLA-2026). Цель конференции — обсуждение современных тенденций в области нелинейного анализа, экстремальных задач и их приложений.',
            'program': 'Пленарные лекции ведущих учёных, секционные доклады молодых исследователей.',
            'requirements': 'Регистрация и подача тезисов на английском языке до 1 мая 2026 г.',
            'participation_terms': 'Без оргвзноса. Участие в гибридном формате (онлайн и очное).',
            'contact_email': 'nla2026@isem.irk.ru',
            'contact_phone': '+7 (3952) 42-71-00',
            'website': 'https://nla2026.isem.irk.ru',
            'is_featured': False,
            'is_free': True,
            'topics': ['Нелинейный анализ', 'Экстремальные задачи', 'Математика'],
        },

        # МГТУ ГА - Гражданская авиация (конференция) [citation:3]
        {
            'title': 'XV Международная научно-техническая конференция «Гражданская авиация на современном этапе развития науки, техники и общества»',
            'short_title': 'ГА-2026',
            'organization': organizations['МГТУ им. Баумана'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 5, 20),
            'end_date': date(2026, 5, 21),
            'deadline': date(2026, 4, 1),
            'location': 'Москва',
            'venue': 'Московский государственный технический университет гражданской авиации',
            'address': 'г. Москва',
            'description': 'XV Международная научно-техническая конференция, посвященная 55-летию МГТУ ГА «Гражданская авиация на современном этапе развития науки, техники и общества». Конференция посвящена актуальным проблемам развития гражданской авиации, авиационной техники и технологий.',
            'program': 'Пленарные доклады, секционные заседания по направлениям: авиационная техника, аэронавигация, экономика и управление на транспорте.',
            'requirements': 'Требования к оформлению на сайте конференции.',
            'contact_email': 'science@mstuca.ru',
            'website': 'https://mstuca.ru/conference2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Авиация', 'Технические науки', 'Управление летательными аппаратами'],
        },

        # Молодежь. Техника. Космос (конференция) [citation:3]
        {
            'title': 'XVIII Международная молодежная научно-техническая конференция «Молодежь. Техника. Космос»',
            'short_title': 'МТК-2026',
            'organization': organizations['МГТУ им. Баумана'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 3, 30),
            'end_date': date(2026, 4, 2),
            'deadline': date(2026, 2, 15),
            'location': 'Санкт-Петербург',
            'venue': 'Балтийский государственный технический университет «ВОЕНМЕХ»',
            'address': 'г. Санкт-Петербург',
            'description': 'XVIII Международная молодежная научно-техническая конференция «Молодежь. Техника. Космос». Мероприятие объединяет молодых ученых, аспирантов и студентов, работающих в области ракетно-космической техники и технологий.',
            'program': 'Секционные заседания по ракетно-космической технике, приборостроению, информационным технологиям.',
            'requirements': 'Требования на сайте конференции.',
            'contact_email': 'youth@voenmeh.ru',
            'website': 'https://www.voenmeh.ru/conference2026',
            'is_featured': False,
            'is_free': True,
            'topics': ['Космонавтика', 'Технические науки', 'Информатика'],
        },

        # Супервычисления и математическое моделирование (конференция) [citation:3]
        {
            'title': 'XX Международная конференция «Супервычисления и математическое моделирование»',
            'short_title': 'СММ-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 10, 5),
            'end_date': date(2026, 10, 9),
            'deadline': date(2026, 8, 1),
            'location': 'Саров',
            'venue': 'РФЯЦ-ВНИИЭФ',
            'address': 'г. Саров, Нижегородская обл.',
            'description': 'XX Международная конференция «Супервычисления и математическое моделирование». Конференция посвящена развитию методов математического моделирования и суперкомпьютерных технологий для решения фундаментальных и прикладных задач.',
            'program': 'Пленарные доклады ведущих ученых, секционные заседания, школа для молодых ученых.',
            'requirements': 'Требования на сайте конференции. Рабочие языки: русский, английский.',
            'requirements_link': 'https://conf.vniief.ru/supercomputing',
            'contact_email': 'super@vniief.ru',
            'website': 'https://conf.vniief.ru/supercomputing',
            'is_featured': True,
            'is_free': False,
            'topics': ['Супервычисления', 'Математическое моделирование', 'Информатика'],
        },

        # ИЗК СО РАН - Сейсмическая безопасность (конференция) [citation:5]
        {
            'title': 'XVII Российская национальная конференция по сейсмической безопасности и снижению риска бедствий',
            'short_title': 'Сейсмобезопасность-2026',
            'organization': organizations['ИЗК СО РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 3, 10),
            'end_date': date(2026, 3, 12),
            'deadline': date(2026, 2, 1),
            'location': 'Иркутск',
            'venue': 'Институт земной коры СО РАН',
            'address': 'г. Иркутск, ул. Лермонтова, д. 128',
            'description': 'XVII Российская национальная конференция по сейсмической безопасности и снижению риска бедствий. Пленарное заседание во Дворце Молодежи Иркутской области, панельные секции и круглый стол на базе Института земной коры СО РАН.',
            'program': 'Пленарное заседание, панельные секции, круглый стол по вопросам сейсмической безопасности.',
            'requirements': 'Требования на сайте конференции.',
            'contact_email': 'conference@crust.irk.ru',
            'website': 'https://www.crust.irk.ru/seismo2026',
            'is_featured': True,
            'is_free': False,
            'topics': ['Сейсмология', 'Сейсмическая безопасность', 'Геология', 'Геофизика'],
        },

        # Медицинская химия (конференция) [citation:5]
        {
            'title': '7-я Российская конференция по медицинской химии',
            'short_title': 'МедХим-Россия 2026',
            'organization': organizations['СО РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 8, 24),
            'end_date': date(2026, 8, 28),
            'deadline': date(2026, 5, 1),
            'location': 'пос. Большое Голоустное, Иркутская обл.',
            'venue': 'Байкал, база отдыха',
            'address': 'п. Большое Голоустное, Иркутская обл.',
            'description': 'Организационный комитет конференции МедХим-Россия 2026 приглашает академических и университетских исследователей, зарубежных ученых, представителей фармацевтического бизнеса и медицины, аспирантов и студентов принять участие в 7-й Российской конференции по медицинской химии на берегу озера Байкал.',
            'program': 'Секции по медицинской химии, фармакологии, дизайну лекарственных средств.',
            'requirements': 'Регистрация и подача тезисов до 1 мая 2026 г.',
            'contact_email': 'medchem2026@irioch.ru',
            'website': 'https://medchem2026.sbras.ru',
            'is_featured': True,
            'is_free': False,
            'topics': ['Медицинская химия', 'Химия', 'Медицина'],
        },

        # Геология и минеральные ресурсы Северо-Востока России (конференция) [citation:5]
        {
            'title': 'XVI Международная научно-практическая конференция «Геология и минерально-сырьевые ресурсы Северо-Востока России»',
            'short_title': 'Геология-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 3, 23),
            'end_date': date(2026, 3, 26),
            'deadline': date(2026, 2, 1),
            'location': 'Иркутск',
            'venue': 'Институт земной коры СО РАН',
            'address': 'г. Иркутск',
            'description': 'XVI Международная научно-практическая конференция «Геология и минерально-сырьевые ресурсы Северо-Востока России». Конференция посвящена 135-летнему юбилею со дня рождения член-корреспондента АН СССР Сергея Владимировича Обручева. Ведущие ученые в области наук о Земле обсудят вопросы геологии, геокриологии, экологии, добычи полезных ископаемых на территории Северо-востока РФ.',
            'program': 'Секции по геологии, геокриологии, экологии, добыче полезных ископаемых.',
            'requirements': 'Требования на сайте конференции.',
            'contact_email': 'geo2026@crust.irk.ru',
            'website': 'https://www.crust.irk.ru/geo2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Геология', 'Геология и минеральные ресурсы', 'Науки о Земле'],
        },

        # Микробиология (конференция) [citation:5]
        {
            'title': 'IV Всероссийская конференция с международным участием «Механизмы адаптации микроорганизмов к различным условиям среды обитания»',
            'short_title': 'MICRAD-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 8, 24),
            'end_date': date(2026, 8, 29),
            'deadline': date(2026, 5, 1),
            'location': 'Иркутск / оз. Байкал',
            'venue': 'Турбаза Уюга',
            'address': 'п. Большое Голоустное, Иркутская обл.',
            'description': 'IV Всероссийская конференция с международным участием «Механизмы адаптации микроорганизмов к различным условиям среды обитания – MICRAD-2026» на берегу озера Байкал.',
            'program': 'Секции по микробиологии, молекулярной биологии, адаптации микроорганизмов.',
            'requirements': 'Требования на сайте конференции.',
            'contact_email': 'micrad2026@lin.irk.ru',
            'website': 'https://micrad2026.lin.irk.ru',
            'is_featured': False,
            'is_free': False,
            'topics': ['Микробиология', 'Биология', 'Молекулярная биология'],
        },

        # Региональная энергетическая политика (конференция) [citation:5]
        {
            'title': 'V Всероссийская конференция «Региональная энергетическая политика»',
            'short_title': 'РЭП-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 6, 15),
            'end_date': date(2026, 6, 18),
            'deadline': date(2026, 4, 1),
            'location': 'Иркутск, п. Никола',
            'venue': 'Байкал',
            'address': 'Иркутский р-н, п. Никола',
            'description': 'V Всероссийская конференция «Региональная энергетическая политика». Цель конференции — обсуждение актуальных проблем региональной энергетической политики, энергосбережения и повышения энергоэффективности.',
            'program': 'Пленарные доклады, секционные заседания, круглые столы.',
            'requirements': 'Требования на сайте конференции.',
            'contact_email': 'energy@isem.irk.ru',
            'website': 'https://energy2026.isem.irk.ru',
            'is_featured': False,
            'is_free': False,
            'topics': ['Энергетика', 'Энергетическая политика', 'Экономика'],
        },

        # МГУ - Инновации в геологии, геофизике и географии
        {
            'title': 'XI Международная научно-практическая конференция «Инновации в геологии, геофизике и географии-2026»',
            'short_title': 'Инновации-2026',
            'organization': organizations['МГУ'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'hybrid',
            'start_date': date(2026, 6, 30),
            'end_date': date(2026, 7, 3),
            'deadline': date(2026, 5, 1),
            'location': 'Москва, МГУ',
            'venue': 'Геологический факультет МГУ',
            'address': '119234, г. Москва, Ленинские горы, д. 1',
            'description': 'Конференция посвящена инновационным методам в геологии, геофизике и географии. Включает секции по малоглубинным геофизическим исследованиям, проблемам Арктического региона, геодинамике, трещиноватости горных пород, грязевому вулканизму, искусственному интеллекту в науках о Земле, криосфере и цифровым двойникам.',
            'program': 'Пленарное заседание, круглые столы, секционные заседания по 14 научным направлениям.',
            'requirements': 'Тезисы докладов принимаются в формате PDF. Объем: 2-4 страницы.',
            'requirements_link': 'https://inno-earthscience-conf.ru/requirements',
            'participation_terms': 'Организационный взнос: для представителей организаций - 8500 руб., для вузов и институтов РАН - 3000 руб., для студентов - 1000 руб.',
            'contact_email': 'innoearthscience@yandex.ru',
            'contact_phone': '+7 (495) 939-10-00',
            'website': 'https://inno-earthscience-conf.ru',
            'is_featured': True,
            'is_free': False,
            'topics': ['Геология', 'Геофизика', 'География', 'Арктические исследования', 'Криосфера',
                       'Искусственный интеллект'],
        },

        # СПбГУ - Беломорская студенческая научная сессия
        {
            'title': 'Беломорская студенческая научная сессия СПбГУ — 2026',
            'short_title': 'Беломорская сессия-2026',
            'organization': organizations['СПбГУ'],
            'event_type': 'school',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 2, 3),
            'end_date': date(2026, 2, 5),
            'deadline': date(2025, 11, 14),
            'location': 'Санкт-Петербург, СПбГУ',
            'venue': 'СПбГУ',
            'address': '199034, г. Санкт-Петербург, Университетская наб., д. 7-9',
            'description': 'Конференция посвящена исследованиям, связанным с Арктическим регионом. Площадка для молодых учёных, где они могут поделиться результатами своих оригинальных исследований. Для студентов младших курсов — возможность попробовать силы в формате постерного или устного доклада.',
            'program': 'Устные и постерные доклады студентов, аспирантов и молодых учёных (до 30 лет). Рабочие языки: русский, английский.',
            'requirements': 'Требования к оформлению тезисов на сайте конференции.',
            'requirements_link': 'https://events.spbu.ru/session-2026/requirements',
            'participation_terms': 'Участие только в очном формате. Каждый участник может представить один доклад в качестве основного автора.',
            'contact_email': 'a.v.kudryavtseva@spbu.ru',
            'contact_phone': '+7 (812) 363-60-44',
            'website': 'https://events.spbu.ru/session-2026',
            'is_featured': False,
            'is_free': True,
            'topics': ['Арктические исследования', 'География', 'Биология', 'Науки о Земле'],
        },

        # МФТИ - Функциональные материалы
        {
            'title': 'II Международная научная конференция «Перспективные функциональные материалы для цифровой и квантовой электроники 2026»',
            'short_title': 'PFM-2026',
            'organization': organizations['МФТИ'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'hybrid',
            'start_date': date(2026, 9, 14),
            'end_date': date(2026, 9, 18),
            'deadline': date(2026, 6, 1),
            'location': 'Московская обл., Долгопрудный',
            'venue': 'МФТИ',
            'address': '141701, Московская обл., г. Долгопрудный, Институтский пер., д. 9',
            'description': 'Конференция посвящена перспективным функциональным материалам для цифровой и квантовой электроники. Ведущие учёные и специалисты обсуждают последние достижения в области материаловедения и квантовых технологий.',
            'program': 'Пленарные доклады, секционные заседания, постерная сессия.',
            'requirements': 'Тезисы докладов принимаются до 1 июня 2026 г.',
            'requirements_link': 'https://mipt.ru/conferences/functional-materials-2026/requirements',
            'participation_terms': 'Организационный взнос для участников: 5000 руб. Для студентов и аспирантов: 2500 руб.',
            'contact_email': 'science@mipt.ru',
            'contact_phone': '+7 (495) 408-45-54',
            'website': 'https://mipt.ru/conferences/functional-materials-2026',
            'is_featured': True,
            'is_free': False,
            'topics': ['Функциональные материалы', 'Физика полупроводников', 'Квантовая физика', 'Материаловедение'],
        },

        # НИУ ВШЭ - Языки, образование, развитие
        {
            'title': 'V Международная научно-практическая конференция «Языки, образование, развитие»',
            'short_title': 'LED Conference 2026',
            'organization': organizations['НИУ ВШЭ'],
            'event_type': 'conference',
            'format': 'online',
            'participation_format': 'online',
            'start_date': date(2026, 4, 20),
            'end_date': date(2026, 4, 21),
            'deadline': date(2026, 3, 1),
            'location': 'Онлайн',
            'venue': 'Платформа НИУ ВШЭ',
            'address': 'Онлайн',
            'description': 'Конференция объединяет экспертов ведущих образовательных, научных и бизнес-организаций со всего мира, а также студентов и аспирантов для обсуждения современных задач и вопросов в сфере лингвистики. Три направления: языки, образование, развитие.',
            'program': 'Направления: фундаментальная и прикладная лингвистика, теория и практика обучения иностранным языкам, РКИ, современные тенденции языкового образования с учётом развития ИИ.',
            'requirements': 'Требования к оформлению тезисов на сайте конференции.',
            'requirements_link': 'https://ling.hse.ru/ledconf/requirements',
            'participation_terms': 'Участие бесплатное. По итогам выпуск сборника статей (РИНЦ).',
            'contact_email': 'ledconf@hse.ru',
            'contact_phone': '+7 (495) 771-32-32',
            'website': 'https://ling.hse.ru/ledconf',
            'is_featured': True,
            'is_free': True,
            'topics': ['Лингвистика', 'Иностранные языки', 'Образование', 'Гуманитарные науки'],
        },

        # Технопром-2026 (форум) [citation:6]
        {
            'title': 'Международный форум «Технопром-2026»',
            'short_title': 'Технопром-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'forum',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 6, 15),
            'end_date': date(2026, 6, 18),
            'deadline': date(2026, 5, 1),
            'location': 'Новосибирск',
            'venue': 'Экспоцентр Новосибирск',
            'address': 'г. Новосибирск, ул. Станционная, 104',
            'description': 'Международный форум «Технопром-2026». Главная тема — «Российская наука — основа технологического лидерства». Участники обсудят ключевые направления развития экономики от искусственного интеллекта и энергетики до медицины будущего и биоинженерии.',
            'program': 'Национальный форум трансфера технологий, Сибирская венчурная ярмарка, международный форум сотрудничества Россия — Африка.',
            'requirements_link': 'https://форумтехнопром.рф/participants',
            'participation_terms': 'Подробная программа и регистрация на официальном сайте.',
            'contact_email': 'info@technoprom.ru',
            'website': 'https://форумтехнопром.рф',
            'is_featured': True,
            'is_free': False,
            'topics': ['Технические науки', 'Информатика', 'Искусственный интеллект', 'Медицина', 'Энергетика'],
        },

        # АлтГУ - Круглый стол по фронтирным территориям [citation:8]
        {
            'title': 'Всероссийский круглый стол «Фронтирные территории: социо-культурные и географические пространства пограничных исследований»',
            'short_title': 'Фронтир-2026',
            'organization': organizations['АлтГУ'],
            'event_type': 'round_table',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2026, 10, 15),
            'end_date': date(2026, 10, 16),
            'deadline': date(2026, 9, 1),
            'location': 'Барнаул',
            'venue': 'Алтайский государственный университет',
            'address': '656049, г. Барнаул, проспект Ленина, д. 61',
            'description': 'Всероссийский круглый стол «Фронтирные территории: социо-культурные и географические пространства пограничных исследований». Мероприятие проводится Институтом гуманитарных наук АлтГУ при участии ФГБОУ ВО «РОСБИОТЕХ».',
            'program': 'Доклады и дискуссии по социо-культурным и географическим аспектам исследования фронтирных территорий.',
            'requirements': 'Заявки принимаются до 1 сентября 2026 г.',
            'participation_terms': 'Предполагаемое число участников: 50, в т.ч. иногородних - 10.',
            'contact_email': 'omelchenko@socio.asu.ru',
            'contact_phone': '8 (913) 214-81-19',
            'contact_person': 'Омельченко Д.А.',
            'website': 'http://events.asu.ru/?event=999',
            'is_featured': False,
            'is_free': True,
            'topics': ['Фронтирные территории', 'Гуманитарные науки', 'Социально-гуманитарные науки', 'География'],
        },

        # Синхротронное излучение (конференция) [citation:5]
        {
            'title': 'Международная конференция по исследованиям синхротронного излучения',
            'short_title': 'СИ-2026',
            'organization': organizations['СО РАН'],
            'event_type': 'conference',
            'format': 'hybrid',
            'participation_format': 'hybrid',
            'start_date': date(2026, 6, 15),
            'end_date': date(2026, 6, 19),
            'deadline': date(2026, 5, 1),
            'location': 'Новосибирск / онлайн',
            'venue': 'Институт ядерной физики СО РАН',
            'address': 'г. Новосибирск, проспект Академика Лаврентьева, 11',
            'description': 'Международная конференция по исследованиям синхротронного излучения. Цель конференции — обсуждение современных тенденций и будущих достижений в области исследований синхротронного излучения, включая разработку установок и приборов для пучков, фундаментальные исследования и промышленные применения.',
            'program': 'Пленарные доклады, секционные заседания, постерная сессия. Рабочий язык: английский.',
            'requirements': 'Регистрация и подача тезисов на английском языке до 1 мая 2026 г.',
            'participation_terms': 'Без оргвзноса. Гибридный формат (онлайн и очное участие).',
            'contact_email': 'sr2026@inp.nsk.ru',
            'website': 'https://sr2026.inp.nsk.ru',
            'is_featured': True,
            'is_free': True,
            'topics': ['Синхротронное излучение', 'Физика', 'Технические науки'],
        },

        # Прошедшие конференции (для тестирования фильтров)
        {
            'title': 'XLVII Международная Звенигородская конференция по физике плазмы и УТС',
            'organization': organizations['ОИВТ РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2024, 3, 18),
            'end_date': date(2024, 3, 22),
            'deadline': date(2024, 1, 15),
            'location': 'Московская обл., Звенигород',
            'description': 'Прошедшая конференция по физике плазмы',
            'contact_email': 'plasma@jiht.ru',
            'topics': ['Физика плазмы'],
        },
        {
            'title': 'XIII ВСЕРОССИЙСКАЯ КОНФЕРЕНЦИЯ ПО ФИЗИЧЕСКОЙ ЭЛЕКТРОНИКЕ',
            'organization': organizations['ОИВТ РАН'],
            'event_type': 'conference',
            'format': 'offline',
            'participation_format': 'offline',
            'start_date': date(2024, 9, 25),
            'end_date': date(2024, 9, 29),
            'deadline': date(2024, 9, 9),
            'location': 'Махачкала, ДГУ',
            'description': 'Прошедшая конференция по физической электронике',
            'contact_email': 'conferences@jiht.ru',
            'topics': ['Физика'],
        },
    ]

    conferences = []

    for conf_data in conferences_data:
        topics_list = conf_data.pop('topics', [])

        title = conf_data['title']
        organization = conf_data['organization']

        # Устанавливаем статус в зависимости от дат
        today = date.today()
        if 'start_date' in conf_data and 'end_date' in conf_data:
            if conf_data['end_date'] < today:
                conf_data['status'] = Conference.Status.ARCHIVED
            elif conf_data['start_date'] <= today <= conf_data['end_date']:
                conf_data['status'] = Conference.Status.PUBLISHED
            else:
                conf_data['status'] = Conference.Status.PUBLISHED
        else:
            conf_data['status'] = Conference.Status.PUBLISHED

        # Добавляем поля по умолчанию
        if 'short_title' not in conf_data:
            conf_data['short_title'] = ''
        if 'venue' not in conf_data:
            conf_data['venue'] = ''
        if 'address' not in conf_data:
            conf_data['address'] = ''
        if 'program' not in conf_data:
            conf_data['program'] = ''
        if 'requirements' not in conf_data:
            conf_data['requirements'] = ''
        if 'requirements_link' not in conf_data:
            conf_data['requirements_link'] = ''
        if 'requirements_file' not in conf_data:
            conf_data['requirements_file'] = None
        if 'participation_terms' not in conf_data:
            conf_data['participation_terms'] = ''
        if 'contact_phone' not in conf_data:
            conf_data['contact_phone'] = ''
        if 'contact_person' not in conf_data:
            conf_data['contact_person'] = ''
        if 'website' not in conf_data:
            conf_data['website'] = ''
        if 'call_for_papers' not in conf_data:
            conf_data['call_for_papers'] = ''
        if 'poster' not in conf_data:
            conf_data['poster'] = None
        if 'is_featured' not in conf_data:
            conf_data['is_featured'] = False
        if 'is_free' not in conf_data:
            conf_data['is_free'] = True
        if 'has_publications' not in conf_data:
            conf_data['has_publications'] = True
        if 'publication_indexing' not in conf_data:
            conf_data['publication_indexing'] = ''
        if 'participation_format' not in conf_data:
            conf_data['participation_format'] = Conference.ParticipationFormat.HYBRID

        conf, created = Conference.objects.get_or_create(
            title=title,
            organization=organization,
            defaults=conf_data
        )

        if created:
            for topic_name in topics_list:
                if topic_name in topics:
                    conf.topics.add(topics[topic_name])
            conf.save()
            print_success(
                f"Создано мероприятие: {conf.title[:60]}... ({conf.organization.short_name}) - {conf.get_event_type_display()}")
            conferences.append(conf)
        else:
            print_info(f"Мероприятие уже существует: {conf.title[:40]}...")

    return conferences


def create_additional_users():
    """Создание дополнительных пользователей (участников)"""
    print_header("СОЗДАНИЕ ТЕСТОВЫХ УЧАСТНИКОВ")

    users_data = [
        {
            'username': 'ivanov_ii',
            'email': 'ivan.ivanov@phd.ru',
            'password': 'Test123!@#',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'middle_name': 'Иванович',
            'affiliation': 'МГУ им. М.В. Ломоносова, Физический факультет',
            'academic_degree': 'phd_student',
        },
        {
            'username': 'petrova_ma',
            'email': 'maria.petrova@science.ru',
            'password': 'Science2024!',
            'first_name': 'Мария',
            'last_name': 'Петрова',
            'middle_name': 'Александровна',
            'affiliation': 'СПбГУ, Институт наук о Земле',
            'academic_degree': 'phd',
        },
        {
            'username': 'smirnov_student',
            'email': 'alexey.smirnov@student.ru',
            'password': 'Student2025!',
            'first_name': 'Алексей',
            'last_name': 'Смирнов',
            'middle_name': '',
            'affiliation': 'МФТИ, Физтех-школа физики',
            'academic_degree': 'student',
        },
        {
            'username': 'kozlov_asp',
            'email': 'dmitry.kozlov@phd.ru',
            'password': 'Aspirant2025!',
            'first_name': 'Дмитрий',
            'last_name': 'Козлов',
            'middle_name': 'Петрович',
            'affiliation': 'НИЯУ МИФИ, Институт ядерной физики',
            'academic_degree': 'phd_student',
        },
        {
            'username': 'sokolova_teacher',
            'email': 'elena.sokolova@teacher.ru',
            'password': 'Teacher2025!',
            'first_name': 'Елена',
            'last_name': 'Соколова',
            'middle_name': 'Викторовна',
            'affiliation': 'Московский педагогический государственный университет',
            'academic_degree': 'teacher',
        },
        {
            'username': 'volkov_phd',
            'email': 'andrey.volkov@science.ru',
            'password': 'Doctor2025!',
            'first_name': 'Андрей',
            'last_name': 'Волков',
            'middle_name': 'Сергеевич',
            'affiliation': 'ФТИ им. А.Ф. Иоффе, Лаборатория физики полупроводников',
            'academic_degree': 'phd',
        },
        {
            'username': 'mikhailova_prof',
            'email': 'nina.mikhailova@academy.ru',
            'password': 'Professor2025!',
            'first_name': 'Нина',
            'last_name': 'Михайлова',
            'middle_name': 'Ивановна',
            'affiliation': 'НИУ ВШЭ, Школа лингвистики',
            'academic_degree': 'prof',
        },
        {
            'username': 'morozov_school',
            'email': 'morozov.school@edu.ru',
            'password': 'School2025!',
            'first_name': 'Илья',
            'last_name': 'Морозов',
            'middle_name': '',
            'affiliation': 'Школа №57, 11 класс',
            'academic_degree': '',
        },
        {
            'username': 'zaitsev_business',
            'email': 'zaitsev@company.ru',
            'password': 'Business2025!',
            'first_name': 'Максим',
            'last_name': 'Зайцев',
            'middle_name': 'Олегович',
            'affiliation': 'ООО "Инновационные технологии", отдел R&D',
            'academic_degree': '',
        },
        {
            'username': 'john_doe',
            'email': 'john.doe@uni.edu',
            'password': 'English2025!',
            'first_name': 'John',
            'last_name': 'Doe',
            'middle_name': '',
            'affiliation': 'MIT, Department of Physics',
            'academic_degree': 'phd',
        },
        {
            'username': 'alekseeva_ms',
            'email': 'maria.alekseeva@science.ru',
            'password': 'Science2026!',
            'first_name': 'Мария',
            'last_name': 'Алексеева',
            'middle_name': 'Сергеевна',
            'affiliation': 'Институт земной коры СО РАН',
            'academic_degree': 'phd',
        },
        {
            'username': 'popov_ai',
            'email': 'a.popov@geology.ru',
            'password': 'Geology2026!',
            'first_name': 'Александр',
            'last_name': 'Попов',
            'middle_name': 'Игоревич',
            'affiliation': 'Алтайский государственный университет',
            'academic_degree': 'phd_student',
        },
        {
            'username': 'semenov_dv',
            'email': 'd.semenov@energy.ru',
            'password': 'Energy2026!',
            'first_name': 'Дмитрий',
            'last_name': 'Семёнов',
            'middle_name': 'Владимирович',
            'affiliation': 'Объединенный институт высоких температур РАН',
            'academic_degree': 'phd',
        },
    ]

    for user_data in users_data:
        password = user_data.pop('password')
        username = user_data['username']

        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults=user_data
        )

        if created:
            user.set_password(password)
            user.email_verified = True
            user.save()
            print_success(f"Создан участник: {user.get_full_name()} ({user.username})")
        else:
            print_info(f"Участник уже существует: {user.username}")


def main():
    """Главная функция"""
    print_header("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ АКТУАЛЬНЫМИ ТЕСТОВЫМИ ДАННЫМИ")
    print_info("Начинаем создание тестовых данных...")

    # Создаем тематики
    topics = create_topics()

    # Проверяем тематики
    check_topic_slugs()

    # Создаем организации
    organizations = create_organizations_and_users()

    # Создаем конференции и мероприятия
    conferences = create_conferences(organizations, topics)

    # Создаем дополнительных участников
    create_additional_users()

    print_header("ИТОГИ ЗАПОЛНЕНИЯ")
    print_success(f"Всего тематик: {Topic.objects.count()}")
    print_success(f"Всего организаций: {Organization.objects.filter(is_active=True).count()}")
    print_success(f"Всего мероприятий: {Conference.objects.count()}")
    print_success(f"Всего пользователей: {CustomUser.objects.count()}")

    # Статистика по типам мероприятий (ИСПРАВЛЕННЫЙ БЛОК)
    print_info("\nСтатистика по типам мероприятий:")
    from django.db.models import Count  # Добавляем импорт здесь
    event_type_counts = Conference.objects.values('event_type').annotate(count=Count('id'))
    for item in event_type_counts:
        event_type = item['event_type']
        count = item['count']
        type_display = dict(Conference.EventType.choices).get(event_type, event_type)
        print_info(f"  {type_display}: {count}")

    print_info(f"Из них организаций-пользователей: {Organization.objects.filter(is_active=True).count()}")
    print_info(
        f"Из них обычных участников: {CustomUser.objects.filter(is_superuser=False, organization__isnull=True).count()}")

    print("\n" + Colors.BOLD + "✅ База данных успешно заполнена актуальными данными на 2026-2027 годы!" + Colors.ENDC)
    print("\nТестовые учетные записи:")
    print("  Организации (логин / пароль):")
    print("  - msu_org / MsuOrg2024! (МГУ)")
    print("  - spbu_org / SpbuOrg2024! (СПбГУ)")
    print("  - mipt_org / MiptOrg2024! (МФТИ)")
    print("  - jiht_org / JihtOrg2024! (ОИВТ РАН)")
    print("  - bmstu_org / Bmstu2026! (МГТУ им. Баумана)")
    print("  - sbras_org / Sbras2026! (СО РАН)")
    print("  - crust_org / Crust2026! (ИЗК СО РАН)")
    print("  - asu_org / Asu2026! (АлтГУ)")

    print("\n  Участники (логин / пароль):")
    print("  - ivanov_ii / Test123!@# (Иван Иванов, МГУ)")
    print("  - petrova_ma / Science2024! (Мария Петрова, СПбГУ)")
    print("  - smirnov_student / Student2025! (Алексей Смирнов, МФТИ)")
    print("  - alekseeva_ms / Science2026! (Мария Алексеева, ИЗК СО РАН)")
    print("  - semenov_dv / Energy2026! (Дмитрий Семёнов, ОИВТ РАН)")

    print("\nАктуальные мероприятия 2026 года:")
    upcoming = Conference.objects.filter(status=Conference.Status.PUBLISHED, start_date__gte=date.today()).order_by(
        'start_date')[:5]
    for conf in upcoming:
        print(f"  • {conf.start_date.strftime('%d.%m')} - {conf.title[:60]}... ({conf.get_event_type_display()})")


if __name__ == '__main__':
    main()
#!/usr/bin/env python
"""
Скрипт для заполнения базы данных тестовыми данными.
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

        # Математика и информатика
        'Математика': 'mathematics',
        'Прикладная математика': 'applied-mathematics',
        'Информатика': 'computer-science',
        'Искусственный интеллект': 'artificial-intelligence',
        'Суперкомпьютерные технологии': 'supercomputing',
        'Цифровизация': 'digitalization',

        # Науки о Земле
        'Науки о Земле': 'earth-sciences',
        'Геология': 'geology',
        'Геофизика': 'geophysics',
        'География': 'geography',
        'Арктические исследования': 'arctic-research',
        'Криосфера': 'cryosphere',

        # Биология и медицина
        'Биология': 'biology',
        'Молекулярная биология': 'molecular-biology',
        'Медицина': 'medicine',

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

        # Гуманитарные науки
        'Гуманитарные науки': 'humanities',
        'Лингвистика': 'linguistics',
        'Образование': 'education',
        'Иностранные языки': 'foreign-languages',

        # Экономика и финансы
        'Экономика': 'economics',
        'Финансы': 'finance',
        'Инвестиции': 'investments',
        'Устойчивое развитие': 'sustainable-development',
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
        {'name': 'Информатика', 'order': 30},
        {'name': 'Искусственный интеллект', 'parent': 'Информатика', 'order': 31},
        {'name': 'Суперкомпьютерные технологии', 'parent': 'Информатика', 'order': 32},
        {'name': 'Цифровизация', 'parent': 'Информатика', 'order': 33},

        # Науки о Земле
        {'name': 'Науки о Земле', 'order': 40},
        {'name': 'Геология', 'parent': 'Науки о Земле', 'order': 41},
        {'name': 'Геофизика', 'parent': 'Науки о Земле', 'order': 42},
        {'name': 'География', 'parent': 'Науки о Земле', 'order': 43},
        {'name': 'Арктические исследования', 'parent': 'Науки о Земле', 'order': 44},
        {'name': 'Криосфера', 'parent': 'Науки о Земле', 'order': 45},

        # Биология и медицина
        {'name': 'Биология', 'order': 50},
        {'name': 'Молекулярная биология', 'parent': 'Биология', 'order': 51},
        {'name': 'Медицина', 'order': 60},

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
        {'name': 'Телекоммуникации', 'parent': 'Технические науки', 'order': 93},
        {'name': 'Радиофотоника', 'parent': 'Технические науки', 'order': 94},

        # Гуманитарные науки
        {'name': 'Гуманитарные науки', 'order': 100},
        {'name': 'Лингвистика', 'parent': 'Гуманитарные науки', 'order': 101},
        {'name': 'Образование', 'parent': 'Гуманитарные науки', 'order': 102},
        {'name': 'Иностранные языки', 'parent': 'Лингвистика', 'order': 103},

        # Экономика и финансы
        {'name': 'Экономика', 'order': 110},
        {'name': 'Финансы', 'parent': 'Экономика', 'order': 111},
        {'name': 'Инвестиции', 'parent': 'Экономика', 'order': 112},
        {'name': 'Устойчивое развитие', 'parent': 'Экономика', 'order': 113},
    ]

    # Сначала создадим все тематики без родителей
    topics_dict = {}
    for topic_data in topics_data:
        if 'parent' not in topic_data:
            # Получаем slug из словаря или генерируем
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

            # Если тематика уже существует, но slug неправильный - обновляем
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

                # Если тематика уже существует, но slug неправильный - обновляем
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

    # Проверка на дубликаты
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
        # МГУ
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
                'description': 'МГУ имени М.В. Ломоносова — крупнейший классический университет Российской Федерации, один из центров отечественной науки и культуры. В университете регулярно проводятся международные и всероссийские научные конференции по самым разным направлениям.',
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
                'description': 'СПбГУ — старейший университет России, основанный в 1724 году. Проводит широкий спектр научных мероприятий, включая знаменитую Беломорскую студенческую научную сессию.',
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
                'description': 'МФТИ — ведущий технический вуз России, готовящий специалистов в области теоретической и экспериментальной физики, математики и информатики. Проводит конференции по функциональным материалам и квантовой электронике.',
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
                'description': 'НИЯУ МИФИ — один из ведущих технических университетов России, специализирующийся на ядерной физике, информационных технологиях и материаловедении. Организует конференцию "Финатлон форум" по финансовым технологиям.',
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
                'description': 'ФТИ им. А.Ф. Иоффе — один из крупнейших научно-исследовательских институтов России в области физики. Проводит множество конференций по физике полупроводников, сегнетоэлектриков, люминесценции и наноуглероду.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # ИФВЭ (Протвино)
        {
            'username': 'ihep_org',
            'password': 'IhepOrg2024!',
            'user_data': {
                'email': 'science@ihep.ru',
                'first_name': 'Николай',
                'last_name': 'Тюрин',
                'affiliation': 'ИФВЭ',
            },
            'org_data': {
                'name': 'Институт физики высоких энергий имени А.А. Логунова НИЦ «Курчатовский институт»',
                'short_name': 'ИФВЭ',
                'inn': '5037012345',
                'kpp': '503701001',
                'legal_address': '142281, Московская обл., г. Протвино, пл. Науки, д. 1',
                'contact_person': 'Тюрин Николай Евгеньевич',
                'contact_position': 'Председатель оргкомитета',
                'contact_email': 'science@ihep.ru',
                'contact_phone': '+7 (4967) 74-20-20',
                'website': 'https://www.ihep.ru',
                'description': 'ИФВЭ — ведущий российский центр в области физики высоких энергий. На базе ускорительного комплекса У-70 проводит конференции по физике частиц при средних и высоких энергиях.',
                'is_active': True,
                'is_verified': True,
            }
        },
        # ОИВТ РАН
        {
            'username': 'jiht_org',
            'password': 'JihtOrg2024!',
            'user_data': {
                'email': 'conferences@jiht.ru',
                'first_name': 'Владимир',
                'last_name': 'Фортов',
                'affiliation': 'ОИВТ РАН',
            },
            'org_data': {
                'name': 'Объединенный институт высоких температур РАН',
                'short_name': 'ОИВТ РАН',
                'inn': '7728012345',
                'kpp': '772801001',
                'legal_address': '125412, г. Москва, ул. Ижорская, д. 13, стр. 2',
                'contact_person': 'Фортов Владимир Евгеньевич',
                'contact_position': 'Научный руководитель',
                'contact_email': 'conferences@jiht.ru',
                'contact_phone': '+7 (495) 484-23-33',
                'website': 'https://jiht.ru',
                'description': 'ОИВТ РАН проводит фундаментальные и прикладные исследования в области физики плазмы, энергетики, теплофизики. Организует Звенигородские конференции по физике плазмы и УТС, а также конференции по молекулярной динамике.',
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
        # УУНиТ (Уфа)
        {
            'username': 'uust_org',
            'password': 'UustOrg2024!',
            'user_data': {
                'email': 'science@uust.ru',
                'first_name': 'Владимир',
                'last_name': 'Захаров',
                'affiliation': 'УУНиТ',
            },
            'org_data': {
                'name': 'Уфимский университет науки и технологий',
                'short_name': 'УУНиТ',
                'inn': '0274012345',
                'kpp': '027401001',
                'legal_address': '450076, г. Уфа, ул. Заки Валиди, д. 32',
                'contact_person': 'Захаров Владимир Петрович',
                'contact_position': 'Ректор',
                'contact_email': 'science@uust.ru',
                'contact_phone': '+7 (347) 272-63-70',
                'website': 'https://uust.ru',
                'description': 'УУНиТ — крупнейший вуз Башкортостана, образованный путем объединения БашГУ и УГАТУ. Проводит международную конференцию по телекоммуникациям и информационным технологиям совместно с ведущими вузами и предприятиями.',
                'is_active': True,
                'is_verified': True,
            }
        },
    ]

    organizations = {}

    for org_info in organizations_data:
        # Создаем или получаем пользователя
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

        # Создаем или получаем организацию
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


def create_additional_organizations():
    """Создание дополнительных организаций из новых источников"""
    print_header("ДОБАВЛЕНИЕ НОВЫХ ОРГАНИЗАЦИЙ")

    new_orgs_data = [
        # ЦИАМ им. П.И. Баранова
        {
            'username': 'ciam_org',
            'password': 'CiamOrg2026!',
            'user_data': {
                'email': 'conference@ciam.ru',
                'first_name': 'Александр',
                'last_name': 'Ланшин',
                'affiliation': 'ЦИАМ им. П.И. Баранова',
            },
            'org_data': {
                'name': 'Центральный институт авиационного моторостроения имени П.И. Баранова',
                'short_name': 'ЦИАМ',
                'inn': '7722012345',
                'kpp': '772201001',
                'legal_address': '111116, г. Москва, ул. Авиамоторная, д. 2',
                'contact_person': 'Ланшин Александр Иванович',
                'contact_position': 'Профессор, организационный комитет',
                'contact_email': 'conference@ciam.ru',
                'contact_phone': '+7 (495) 361-50-00',
                'website': 'https://ciam.ru',
                'description': 'ЦИАМ – единственная российская авиационная научная организация, обладающая уникальной экспериментальной базой для исследований в области авиационного двигателестроения. Институт проводит международные симпозиумы по неравновесным процессам, плазме, горению и атмосферным явлениям совместно с ведущими научными центрами.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # МЦХФ им. Н.Н. Семенова
        {
            'username': 'mchf_org',
            'password': 'MchfOrg2026!',
            'user_data': {
                'email': 'science@chph.ras.ru',
                'first_name': 'Сергей',
                'last_name': 'Фролов',
                'affiliation': 'МЦХФ им. Н.Н. Семенова',
            },
            'org_data': {
                'name': 'Международный центр химической физики им. Н.Н. Семенова',
                'short_name': 'МЦХФ',
                'inn': '7736012345',
                'kpp': '773601001',
                'legal_address': '119991, г. Москва, ул. Косыгина, д. 4',
                'contact_person': 'Фролов Сергей Михайлович',
                'contact_position': 'Профессор, председатель оргкомитета',
                'contact_email': 'science@chph.ras.ru',
                'contact_phone': '+7 (495) 939-74-00',
                'website': 'https://chph.ras.ru',
                'description': 'МЦХФ им. Н.Н. Семенова – ведущий научный центр в области химической физики, основанный нобелевским лауреатом Н.Н. Семеновым. Институт проводит фундаментальные исследования в области горения, взрыва, химической кинетики и физики плазмы.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # НЭБ (Научная электронная библиотека)
        {
            'username': 'elibrary_org',
            'password': 'Elibrary2026!',
            'user_data': {
                'email': 'info@elibrary.ru',
                'first_name': 'Геннадий',
                'last_name': 'Еременко',
                'affiliation': 'НЭБ',
            },
            'org_data': {
                'name': 'Научная электронная библиотека eLIBRARY.RU',
                'short_name': 'НЭБ',
                'inn': '7728012346',
                'kpp': '772801001',
                'legal_address': '121019, г. Москва, ул. Новый Арбат, д. 21',
                'contact_person': 'Еременко Геннадий Олегович',
                'contact_position': 'Генеральный директор',
                'contact_email': 'info@elibrary.ru',
                'contact_phone': '+7 (495) 123-45-67',
                'website': 'https://elibrary.ru',
                'description': 'Научная электронная библиотека eLIBRARY.RU – крупнейший российский информационный портал в области науки, технологии, медицины и образования. Ежегодно проводит международную конференцию SCIENCE ONLINE, посвященную цифровым экосистемам, наукометрии и искусственному интеллекту в научных исследованиях.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # Институт гидродинамики им. М.А. Лаврентьева СО РАН
        {
            'username': 'hydro_org',
            'password': 'Hydro2026!',
            'user_data': {
                'email': 'conference@hydro.nsc.ru',
                'first_name': 'Сергей',
                'last_name': 'Голубев',
                'affiliation': 'ИГиЛ СО РАН',
            },
            'org_data': {
                'name': 'Институт гидродинамики им. М.А. Лаврентьева СО РАН',
                'short_name': 'ИГиЛ СО РАН',
                'inn': '5408112345',
                'kpp': '540801001',
                'legal_address': '630090, г. Новосибирск, пр. Академика Лаврентьева, д. 15',
                'contact_person': 'Голубев Сергей Владимирович',
                'contact_position': 'Ученый секретарь',
                'contact_email': 'conference@hydro.nsc.ru',
                'contact_phone': '+7 (383) 333-12-12',
                'website': 'https://www.hydro.nsc.ru',
                'description': 'ИГиЛ СО РАН – один из ведущих институтов Сибирского отделения РАН в области гидродинамики, физики взрыва, механики сплошных сред. Совместно с ФТИ им. Иоффе проводит международные конференции по наноуглероду и алмазу.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # Академический университет им. Ж.И. Алфёрова
        {
            'username': 'alferov_org',
            'password': 'Alferov2026!',
            'user_data': {
                'email': 'science@spbau.ru',
                'first_name': 'Алексей',
                'last_name': 'Насонов',
                'affiliation': 'Академический университет',
            },
            'org_data': {
                'name': 'Санкт-Петербургский национальный исследовательский Академический университет имени Ж.И. Алфёрова РАН',
                'short_name': 'Академический университет',
                'inn': '7801123456',
                'kpp': '780101001',
                'legal_address': '194021, г. Санкт-Петербург, ул. Хлопина, д. 8, корп. 3',
                'contact_person': 'Насонов Алексей Геннадьевич',
                'contact_position': 'Проректор по научной работе',
                'contact_email': 'science@spbau.ru',
                'contact_phone': '+7 (812) 448-85-00',
                'website': 'https://spbau.ru',
                'description': 'Академический университет им. Ж.И. Алфёрова – уникальный научно-образовательный центр, объединяющий академическую науку и высшее образование. Проводит конференции по нанотехнологиям, физике полупроводников и люминесценции совместно с ФТИ им. Иоффе.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # МГТУ им. Н.Э. Баумана
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
                'description': 'МГТУ им. Н.Э. Баумана – ведущий технический университет России. Является главным организатором Всероссийского форума «Шаг в будущее», который объединяет молодых исследователей и школьников со всей страны. Форум проходит на базе 14 научных центров и 11 университетов.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # МЭИ (Национальный исследовательский университет)
        {
            'username': 'mpei_org',
            'password': 'Mpei2026!',
            'user_data': {
                'email': 'science@mpei.ru',
                'first_name': 'Николай',
                'last_name': 'Рогалев',
                'affiliation': 'НИУ МЭИ',
            },
            'org_data': {
                'name': 'Национальный исследовательский университет «МЭИ»',
                'short_name': 'НИУ МЭИ',
                'inn': '7721012345',
                'kpp': '772101001',
                'legal_address': '111250, г. Москва, ул. Красноказарменная, д. 14',
                'contact_person': 'Рогалев Николай Дмитриевич',
                'contact_position': 'Ректор',
                'contact_email': 'science@mpei.ru',
                'contact_phone': '+7 (495) 362-70-00',
                'website': 'https://mpei.ru',
                'description': 'НИУ МЭИ – ведущий энергетический университет России. Активно участвует в организации Всероссийского форума «Шаг в будущее», проводя секции по цифровой энергетике, экологии техносферы, физическим основам технологий, информационной безопасности и экономике.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # ИОФ РАН (Институт общей физики)
        {
            'username': 'gpi_org',
            'password': 'Gpi2026!',
            'user_data': {
                'email': 'conference@gpi.ru',
                'first_name': 'Сергей',
                'last_name': 'Гарнов',
                'affiliation': 'ИОФ РАН',
            },
            'org_data': {
                'name': 'Институт общей физики им. А.М. Прохорова РАН',
                'short_name': 'ИОФ РАН',
                'inn': '7736012346',
                'kpp': '773601001',
                'legal_address': '119991, г. Москва, ул. Вавилова, д. 38',
                'contact_person': 'Гарнов Сергей Владимирович',
                'contact_position': 'Директор',
                'contact_email': 'conference@gpi.ru',
                'contact_phone': '+7 (499) 503-87-77',
                'website': 'https://www.gpi.ru',
                'description': 'ИОФ РАН им. А.М. Прохорова – ведущий институт в области лазерной физики, фотоники и спектроскопии. Проводит секцию «Общая физика» в рамках Всероссийского форума «Шаг в будущее», объединяя молодых исследователей со всей страны.',
                'is_active': True,
                'is_verified': True,
            }
        },

        # ИМЕТ РАН (Институт металлургии и материаловедения)
        {
            'username': 'imet_org',
            'password': 'Imet2026!',
            'user_data': {
                'email': 'science@imet.ac.ru',
                'first_name': 'Владимир',
                'last_name': 'Комлев',
                'affiliation': 'ИМЕТ РАН',
            },
            'org_data': {
                'name': 'Институт металлургии и материаловедения им. А.А. Байкова РАН',
                'short_name': 'ИМЕТ РАН',
                'inn': '7736012347',
                'kpp': '773601001',
                'legal_address': '119991, г. Москва, Ленинский пр-т, д. 49',
                'contact_person': 'Комлев Владимир Сергеевич',
                'contact_position': 'Директор',
                'contact_email': 'science@imet.ac.ru',
                'contact_phone': '+7 (499) 135-20-60',
                'website': 'https://www.imet.ac.ru',
                'description': 'ИМЕТ РАН им. А.А. Байкова – ведущий институт в области металлургии, материаловедения, наноматериалов и керамики. Проводит секцию «Технологии создания новых материалов» на Всероссийском форуме «Шаг в будущее».',
                'is_active': True,
                'is_verified': True,
            }
        },

        # ИКИ РАН (Институт космических исследований)
        {
            'username': 'iki_org',
            'password': 'Iki2026!',
            'user_data': {
                'email': 'science@cosmos.ru',
                'first_name': 'Анатолий',
                'last_name': 'Петрукович',
                'affiliation': 'ИКИ РАН',
            },
            'org_data': {
                'name': 'Институт космических исследований РАН',
                'short_name': 'ИКИ РАН',
                'inn': '7736012348',
                'kpp': '773601001',
                'legal_address': '117997, г. Москва, ул. Профсоюзная, д. 84/32',
                'contact_person': 'Петрукович Анатолий Алексеевич',
                'contact_position': 'Директор',
                'contact_email': 'science@cosmos.ru',
                'contact_phone': '+7 (495) 333-23-33',
                'website': 'https://www.iki.cosmos.ru',
                'description': 'ИКИ РАН – ведущий институт России в области космических исследований, астрофизики и планетологии. Проводит секцию «Земля и Вселенная» на Всероссийском форуме «Шаг в будущее», привлекая молодых исследователей в космическую науку.',
                'is_active': True,
                'is_verified': True,
            }
        },
    ]

    organizations = {}
    for org_info in new_orgs_data:
        # Создаем пользователя
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
            print_success(f"Создан пользователь: {username}")
        else:
            print_info(f"Пользователь уже существует: {username}")

        # Создаем организацию
        org, created = Organization.objects.get_or_create(
            inn=org_info['org_data']['inn'],
            defaults={
                **org_info['org_data'],
                'user': user
            }
        )

        if created:
            print_success(f"Создана организация: {org.name}")
            organizations[org.short_name] = org
        else:
            print_info(f"Организация уже существует: {org.name}")
            organizations[org.short_name] = org

    return organizations


def create_conferences(organizations, topics):
    """Создание основных конференций"""
    print_header("СОЗДАНИЕ КОНФЕРЕНЦИЙ")

    today = date.today()
    conferences_data = [
        # МГУ - Инновации в геологии, геофизике и географии
        {
            'title': 'XI Международная научно-практическая конференция "Инновации в геологии, геофизике и географии-2026"',
            'organization': organizations['МГУ'],
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 6, 30),
            'end_date': date(2026, 7, 3),
            'deadline': date(2026, 5, 1),
            'location': 'Москва, МГУ, Геологический факультет',
            'venue': 'Геологический факультет МГУ',
            'address': '119234, г. Москва, Ленинские горы, д. 1',
            'description': 'Конференция посвящена инновационным методам в геологии, геофизике и географии. Включает секции по малоглубинным геофизическим исследованиям, проблемам Арктического региона, геодинамике, трещиноватости горных пород, грязевому вулканизму, искусственному интеллекту в науках о Земле, криосфере и цифровым двойникам.',
            'program': 'Пленарное заседание, круглые столы, секционные заседания по 14 научным направлениям.',
            'requirements': 'Тезисы докладов принимаются в формате PDF. Объем: 2-4 страницы. Образец оформления на сайте конференции.',
            'participation_terms': 'Организационный взнос: для представителей организаций - 8500 руб., для вузов и институтов РАН - 3000 руб., для студентов - 1000 руб.',
            'contact_email': 'innoearthscience@yandex.ru',
            'contact_phone': '+7 (495) 939-10-00',
            'contact_person': 'Оргкомитет конференции',
            'website': 'https://inno-earthscience-conf.ru',
            'is_featured': True,
            'is_free': False,
            'topics': ['Геология', 'Геофизика', 'География', 'Арктические исследования', 'Криосфера',
                       'Искусственный интеллект'],
        },

        # СПбГУ - Беломорская студенческая научная сессия
        {
            'title': 'Беломорская студенческая научная сессия СПбГУ — 2026',
            'organization': organizations['СПбГУ'],
            'conference_type': 'university',
            'format': 'offline',
            'start_date': date(2026, 2, 3),
            'end_date': date(2026, 2, 5),
            'deadline': date(2025, 11, 14),
            'location': 'Санкт-Петербург, СПбГУ',
            'venue': 'СПбГУ',
            'address': '199034, г. Санкт-Петербург, Университетская наб., д. 7-9',
            'description': 'Конференция посвящена исследованиям, связанным с Арктическим регионом. Площадка для молодых учёных, где они могут поделиться результатами своих оригинальных исследований. Для студентов младших курсов — возможность попробовать силы в формате постерного или устного доклада.',
            'program': 'Устные и постерные доклады студентов, аспирантов и молодых учёных (до 30 лет). Рабочие языки: русский, английский.',
            'requirements': 'Требования к оформлению тезисов на сайте конференции.',
            'participation_terms': 'Участие только в очном формате. Каждый участник может представить один доклад в качестве основного автора.',
            'contact_email': 'a.v.kudryavtseva@spbu.ru',
            'contact_phone': '+7 (812) 363-60-44',
            'contact_person': 'Кудрявцева Анастасия Валерьевна',
            'website': 'https://events.spbu.ru/session-2026',
            'is_featured': False,
            'is_free': True,
            'topics': ['Арктические исследования', 'География', 'Биология', 'Науки о Земле'],
        },

        # МФТИ - Перспективные функциональные материалы
        {
            'title': 'II Международная научная конференция "Перспективные функциональные материалы для цифровой и квантовой электроники 2026"',
            'organization': organizations['МФТИ'],
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 9, 14),
            'end_date': date(2026, 9, 18),
            'deadline': date(2026, 6, 1),
            'location': 'Московская обл., Долгопрудный, МФТИ',
            'venue': 'МФТИ',
            'address': '141701, Московская обл., г. Долгопрудный, Институтский пер., д. 9',
            'description': 'Конференция посвящена перспективным функциональным материалам для цифровой и квантовой электроники. Ведущие учёные и специалисты обсуждают последние достижения в области материаловедения и квантовых технологий.',
            'program': 'Пленарные доклады, секционные заседания, постерная сессия.',
            'requirements': 'Тезисы докладов принимаются до 1 июня 2026 г. Требования на сайте конференции.',
            'participation_terms': 'Организационный взнос для участников: 5000 руб. Для студентов и аспирантов: 2500 руб.',
            'contact_email': 'science@mipt.ru',
            'contact_phone': '+7 (495) 408-45-54',
            'contact_person': 'Оргкомитет',
            'website': 'https://mipt.ru/conferences/functional-materials-2026',
            'is_featured': True,
            'is_free': False,
            'topics': ['Функциональные материалы', 'Физика полупроводников', 'Квантовая физика', 'Материаловедение'],
        },

        # НИЯУ МИФИ - Финатлон форум
        {
            'title': 'VIII Международная научно-практическая конференция молодых учёных и специалистов «Финатлон форум – Профессионалы будущего»',
            'organization': organizations['НИЯУ МИФИ'],
            'conference_type': 'international',
            'format': 'hybrid',
            'start_date': date(2026, 4, 21),
            'end_date': date(2026, 4, 25),
            'deadline': date(2026, 3, 15),
            'location': 'Москва, НИЯУ МИФИ',
            'venue': 'НИЯУ МИФИ',
            'address': '115409, г. Москва, Каширское шоссе, д. 31',
            'description': 'Конференция посвящена вопросам устойчивого развития, инвестиций и финансовых рисков. Ежегодная площадка для выявления и поддержки талантливой молодёжи. В 2025 году в форуме приняли участие авторы более 1200 научных работ из более чем 140 ведущих вузов России и зарубежья.',
            'program': 'Отборочный дистанционный этап (20 марта – 10 апреля), финальная конференция (21–25 апреля). Лучшие работы публикуются в сборнике РИНЦ.',
            'requirements': 'Требования к оформлению работ на сайте finatlonforum.ru',
            'participation_terms': 'Регистрация и подача работ: 25 февраля – 15 марта 2026 года.',
            'contact_email': 'science.conf@mephi.ru',
            'contact_phone': '+7 (495) 369-04-03',
            'contact_person': 'Оргкомитет',
            'website': 'https://finatlonforum.ru',
            'is_featured': False,
            'is_free': True,
            'topics': ['Экономика', 'Финансы', 'Инвестиции', 'Устойчивое развитие'],
        },

        # ФТИ им. Иоффе - Физика полупроводников
        {
            'title': 'Молодежная конференция по физике полупроводников',
            'organization': organizations['ФТИ им. Иоффе'],
            'conference_type': 'national',
            'format': 'offline',
            'start_date': date(2026, 2, 25),
            'end_date': date(2026, 3, 1),
            'deadline': date(2026, 1, 15),
            'location': 'Ленинградская обл., Зеленогорск',
            'venue': 'Дом отдыха',
            'address': 'Зеленогорск, Санкт-Петербург',
            'description': 'Молодежная конференция по физике полупроводников, организуемая ФТИ им. А.Ф. Иоффе. Молодые учёные представляют свои исследования в области физики полупроводников и наноструктур.',
            'program': 'Устные и постерные доклады молодых учёных. Лекции ведущих специалистов.',
            'requirements': 'Тезисы докладов принимаются до 15 января 2026 г.',
            'participation_terms': 'Участие бесплатное. Проживание и питание за счёт участников.',
            'contact_email': 'conferences@mail.ioffe.ru',
            'contact_phone': '+7 (812) 292-79-29',
            'contact_person': 'Куницына Екатерина Вадимовна',
            'website': 'https://www.ioffe.ru/conferences',
            'is_featured': False,
            'is_free': True,
            'topics': ['Физика полупроводников', 'Физика', 'Материаловедение'],
        },

        # ФТИ им. Иоффе - Сегнетоэлектрики
        {
            'title': 'Всероссийский симпозиум «Актуальные вопросы физики сегнетоэлектриков и родственных соединений»',
            'organization': organizations['ФТИ им. Иоффе'],
            'conference_type': 'national',
            'format': 'offline',
            'start_date': date(2026, 5, 13),
            'end_date': date(2026, 5, 15),
            'deadline': date(2026, 3, 1),
            'location': 'Санкт-Петербург, ФТИ им. Иоффе',
            'venue': 'ФТИ им. А.Ф. Иоффе',
            'address': '194021, г. Санкт-Петербург, Политехническая ул., д. 26',
            'description': 'Симпозиум посвящён актуальным вопросам физики сегнетоэлектриков и родственных соединений. Организаторы: ФТИ им. А.Ф. Иоффе, МИРЭА, СПбО РАН.',
            'program': 'Пленарные и секционные доклады по физике сегнетоэлектриков, диэлектриков, пьезоэлектриков.',
            'requirements': 'Тезисы принимаются до 1 марта 2026 г.',
            'participation_terms': 'Оргвзнос: 4000 руб., для студентов 2000 руб.',
            'contact_email': 'conferences@mail.ioffe.ru',
            'contact_phone': '+7 (812) 297-22-45',
            'contact_person': 'Лушников Сергей Германович',
            'website': 'https://www.ioffe.ru/ferro-2026',
            'is_featured': True,
            'is_free': False,
            'topics': ['Сегнетоэлектрики', 'Физика', 'Материаловедение'],
        },

        # ФТИ им. Иоффе - Наноуглерод и Алмаз
        {
            'title': 'Международная конференция «Наноуглерод и Алмаз»',
            'organization': organizations['ФТИ им. Иоффе'],
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 6, 29),
            'end_date': date(2026, 7, 3),
            'deadline': date(2026, 4, 15),
            'location': 'Санкт-Петербург',
            'venue': 'ФТИ им. А.Ф. Иоффе / Академический университет',
            'address': 'Санкт-Петербург',
            'description': 'Международная конференция по наноуглероду, алмазу и родственным материалам. Организаторы: ФТИ им. А.Ф. Иоффе, ИГиЛ СО РАН, Академический университет им. Ж.И. Алфёрова, СПбГТИ(ТУ).',
            'program': 'Секции по синтезу, характеризации и применению наноуглеродных материалов и алмаза.',
            'requirements': 'Тезисы принимаются до 15 апреля 2026 г.',
            'participation_terms': 'Оргвзнос: 6000 руб., для студентов 3000 руб.',
            'contact_email': 'conferences@mail.ioffe.ru',
            'contact_phone': '+7 (812) 292-73-77',
            'contact_person': 'Воробьёва Ирина Владимировна',
            'website': 'https://www.ioffe.ru/nanocarbon-2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Наноуглерод', 'Материаловедение', 'Физика'],
        },

        # ИФВЭ - Физика частиц
        {
            'title': 'Конференция «Физика частиц при средних и высоких энергиях»',
            'organization': organizations['ИФВЭ'],
            'conference_type': 'national',
            'format': 'hybrid',
            'start_date': date(2026, 6, 2),
            'end_date': date(2026, 6, 5),
            'deadline': date(2026, 4, 1),
            'location': 'Московская обл., Протвино',
            'venue': 'ИФВЭ, здание Отдела теоретической физики',
            'address': 'Московская обл., г. Протвино, пл. Науки, д. 1',
            'description': 'Конференция посвящена обзору экспериментальных исследований фундаментальных свойств материи (физики элементарных частиц) на Ускорительном комплексе У-70 и других отечественных установках, формированию актуальных направлений исследований в среднесрочной перспективе.',
            'program': 'Доклады по основным тематикам (20-30 мин), стендовая секция. Рабочий язык: русский (презентации на русском или английском).',
            'requirements': 'Тезисы докладов принимаются до 1 апреля 2026 г.',
            'participation_terms': 'Участие преимущественно очное, возможно онлайн-подключение. Питание и проживание за счёт участников.',
            'contact_email': 'ppihe2026@ihep.ru',
            'contact_phone': '+7 (4967) 74-20-20',
            'contact_person': 'Тюрин Николай Евгеньевич',
            'website': 'https://indico.ihep.su/e/PPIHE2026',
            'is_featured': True,
            'is_free': True,
            'topics': ['Физика частиц', 'Физика', 'Физика высоких энергий'],
        },

        # ОИВТ РАН - Молекулярная Динамика
        {
            'title': 'II Всероссийская конференция "Молекулярная Динамика 2026"',
            'organization': organizations['ОИВТ РАН'],
            'conference_type': 'national',
            'format': 'offline',
            'start_date': date(2026, 6, 28),
            'end_date': date(2026, 7, 5),
            'deadline': date(2026, 3, 1),
            'location': 'Санкт-Петербург, г. Пушкин',
            'venue': 'Конференц-центр',
            'address': 'г. Пушкин, Санкт-Петербург',
            'description': 'Всероссийская конференция по молекулярной динамике, организуемая ОИВТ РАН. Обсуждение современных методов молекулярного моделирования и их применений в различных областях науки.',
            'program': 'Пленарные лекции, секционные доклады, школы для молодых учёных.',
            'requirements': 'Окончание приёма тезисов докладов: до 1 марта 2026 г.',
            'participation_terms': 'Оргвзнос: 5000 руб. Для студентов и аспирантов: 2500 руб.',
            'contact_email': 'conferences@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'contact_person': 'Оргкомитет',
            'website': 'https://jiht.ru/conferences/md2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Физика', 'Химия', 'Биология', 'Молекулярная биология'],
        },

        # ОИВТ РАН - Физика плазмы
        {
            'title': '53 МЕЖДУНАРОДНАЯ КОНФЕРЕНЦИЯ ПО ФИЗИКЕ ПЛАЗМЫ И УПРАВЛЯЕМОМУ ТЕРМОЯДЕРНОМУ СИНТЕЗУ',
            'organization': organizations['ОИВТ РАН'],
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 3, 16),
            'end_date': date(2026, 3, 20),
            'deadline': date(2025, 11, 10),
            'location': 'Московская обл., Звенигород',
            'venue': 'Пансионат',
            'address': 'г. Звенигород, Московская обл.',
            'description': 'Крупнейшая конференция по физике плазмы и управляемому термоядерному синтезу, традиционно проводимая в Звенигороде. Ведущие учёные и специалисты представляют последние достижения в области физики плазмы, УТС и смежных направлениях.',
            'program': 'Пленарные и секционные доклады, постерная сессия. Основные направления: физика высокотемпературной плазмы, УТС, физические аспекты термоядерных реакторов.',
            'requirements': 'Докладчики должны были заполнить регистрационную форму до 10 ноября 2025 г.',
            'participation_terms': 'Оргвзнос: 8000 руб., для студентов 4000 руб.',
            'contact_email': 'plasma@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'contact_person': 'Оргкомитет',
            'website': 'https://jiht.ru/plasma2026',
            'is_featured': True,
            'is_free': False,
            'topics': ['Физика плазмы', 'Физика', 'Энергетика'],
        },

        # НИУ ВШЭ - Языки, образование, развитие
        {
            'title': 'V Международная научно-практическая конференция «Языки, образование, развитие» (HSE LED Conference)',
            'organization': organizations['НИУ ВШЭ'],
            'conference_type': 'international',
            'format': 'online',
            'start_date': date(2026, 4, 20),
            'end_date': date(2026, 4, 21),
            'deadline': date(2026, 3, 1),
            'location': 'Онлайн',
            'venue': 'Платформа НИУ ВШЭ',
            'address': 'Онлайн',
            'description': 'Конференция объединяет экспертов ведущих образовательных, научных и бизнес-организаций со всего мира, а также студентов и аспирантов для обсуждения современных задач и вопросов в сфере лингвистики. Три направления: языки, образование, развитие.',
            'program': 'Направления: фундаментальная и прикладная лингвистика, теория и практика обучения иностранным языкам, РКИ, современные тенденции языкового образования с учётом развития ИИ.',
            'requirements': 'Требования к оформлению тезисов на сайте конференции.',
            'participation_terms': 'Участие бесплатное. По итогам выпуск сборника статей (РИНЦ).',
            'contact_email': 'ledconf@hse.ru',
            'contact_phone': '+7 (495) 771-32-32',
            'contact_person': 'Зырянова Елена Сергеевна',
            'website': 'https://ling.hse.ru/ledconf',
            'is_featured': True,
            'is_free': True,
            'topics': ['Лингвистика', 'Иностранные языки', 'Образование', 'Гуманитарные науки'],
        },

        # УУНиТ - Телекоммуникации
        {
            'title': 'Международная научно-техническая конференция по телекоммуникациям и информационным технологиям',
            'organization': organizations['УУНиТ'],
            'conference_type': 'international',
            'format': 'hybrid',
            'start_date': date(2026, 10, 12),
            'end_date': date(2026, 10, 15),
            'deadline': date(2026, 7, 1),
            'location': 'Уфа, УУНиТ',
            'venue': 'Уфимский университет науки и технологий',
            'address': '450076, г. Уфа, ул. Заки Валиди, д. 32',
            'description': 'Конференция, объединяющая ведущие вузы и предприятия в области телекоммуникаций и информационных технологий. Соорганизаторы: ПГУТИ, КНИТУ-КАИ, БГМУ, АО НПП «Полигон», ПАО «Башинформсвязь», ООО «Газпром Трансгаз Уфа», Сколтех и другие.',
            'program': 'Пленарные доклады, секционные заседания, круглые столы с участием представителей бизнеса и промышленности.',
            'requirements': 'Тезисы докладов принимаются до 1 июля 2026 г.',
            'participation_terms': 'Оргвзнос: 7000 руб., для студентов 3000 руб.',
            'contact_email': 'science@uust.ru',
            'contact_phone': '+7 (347) 272-63-70',
            'contact_person': 'Султанов Альберт Ханович',
            'website': 'https://uust.ru/ptitt',
            'is_featured': True,
            'is_free': False,
            'topics': ['Телекоммуникации', 'Информатика', 'Радиофотоника', 'Технические науки'],
        },

        # Прошедшие конференции (для тестирования фильтров)
        {
            'title': 'XLVII Международная Звенигородская конференция по физике плазмы и УТС',
            'organization': organizations['ОИВТ РАН'],
            'conference_type': 'international',
            'format': 'offline',
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
            'conference_type': 'national',
            'format': 'offline',
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

        # Проверяем, существует ли уже конференция
        title = conf_data['title']
        organization = conf_data['organization']

        # Устанавливаем статус в зависимости от дат
        today = date.today()
        if 'start_date' in conf_data:
            if conf_data['end_date'] < today:
                conf_data['status'] = Conference.Status.ARCHIVED
            elif conf_data['start_date'] <= today <= conf_data['end_date']:
                conf_data['status'] = Conference.Status.PUBLISHED
            else:
                conf_data['status'] = Conference.Status.PUBLISHED
        else:
            conf_data['status'] = Conference.Status.PUBLISHED

        # Добавляем поля по умолчанию, если их нет
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
        if 'participation_terms' not in conf_data:
            conf_data['participation_terms'] = ''
        if 'contact_phone' not in conf_data:
            conf_data['contact_phone'] = ''
        if 'contact_person' not in conf_data:
            conf_data['contact_person'] = ''
        if 'website' not in conf_data:
            conf_data['website'] = ''
        if 'is_featured' not in conf_data:
            conf_data['is_featured'] = False
        if 'is_free' not in conf_data:
            conf_data['is_free'] = True

        conf, created = Conference.objects.get_or_create(
            title=title,
            organization=organization,
            defaults=conf_data
        )

        if created:
            # Добавляем тематики
            for topic_name in topics_list:
                if topic_name in topics:
                    conf.topics.add(topics[topic_name])
            conf.save()
            print_success(f"Создана конференция: {conf.title[:60]}... ({conf.organization.short_name})")
            conferences.append(conf)
        else:
            print_info(f"Конференция уже существует: {conf.title[:40]}...")

    return conferences


def create_additional_conferences(organizations, topics):
    """Создание дополнительных конференций из новых источников"""
    print_header("ДОБАВЛЕНИЕ НОВЫХ КОНФЕРЕНЦИЙ")

    today = date.today()
    new_conferences_data = [
        # 1. Неравновесные процессы, плазма, горение и атмосферные явления (ЦИАМ + МЦХФ)
        {
            'title': '12 Международный симпозиум «Неравновесные процессы, плазма, горение и атмосферные явления»',
            'organization': organizations.get('ЦИАМ') or organizations.get('МЦХФ'),
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 10, 5),
            'end_date': date(2026, 10, 9),
            'deadline': date(2026, 6, 1),
            'location': 'Сочи, Адлер',
            'venue': 'Отель',
            'address': 'г. Сочи, Адлерский район, Россия',
            'description': 'Международный симпозиум, посвященный неравновесным процессам, физике плазмы, горению и атмосферным явлениям. Организаторы: НП МЦХФ им. Н.Н. Семенова и ЦИАМ им. П.И. Баранова. В программный комитет входят ведущие учёные из России, Беларуси и Великобритании.',
            'program': 'Пленарные доклады, секционные заседания по физике плазмы, горению, неравновесным процессам, атмосферным явлениям.',
            'requirements': 'Требования к оформлению тезисов на сайте симпозиума.',
            'participation_terms': 'Оргвзнос уточняется на сайте мероприятия.',
            'contact_email': 'nepcap2024@ciam.ru',
            'contact_phone': '+7 (495) 361-50-00',
            'contact_person': 'Ланшин Александр Иванович',
            'website': 'http://nepcap2024.ciam.ru',
            'is_featured': True,
            'is_free': False,
            'topics': ['Физика плазмы', 'Физика', 'Химия', 'Технические науки'],
        },

        # 2. SCIENCE ONLINE XXIII (НЭБ)
        {
            'title': 'XXIII Международная конференция SCIENCE ONLINE «Наука в цифре: новые горизонты оценки исследований и искусственный интеллект»',
            'organization': organizations.get('НЭБ'),
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 9, 26),
            'end_date': date(2026, 10, 3),
            'deadline': date(2026, 8, 24),
            'location': 'Сочи, Роза-Хутор',
            'venue': 'Golden Tulip 4*',
            'address': 'Сочи, курорт Роза-Хутор, Россия',
            'description': 'Главное событие в сфере информационного сопровождения науки, образования и инновационных отраслей промышленности. Конференция собирает руководителей университетов, академических институтов, издателей, библиотекарей, специалистов по наукометрии и ИИ. Тема 2026 года: "Наука в цифре: новые горизонты оценки исследований и искусственный интеллект".',
            'program': 'Секции: цифровые экосистемы для научных исследований, аналитические инструменты и ИИ в наукометрии, этические аспекты внедрения ИИ, открытая наука, роль научных библиотек, презентация новых продуктов eLIBRARY.RU.',
            'requirements': 'Заявки на выступления принимаются до 15 августа 2026 г.',
            'participation_terms': 'Участие платное. Регистрация до 24 августа 2026 г.',
            'contact_email': 'info@elibrary.ru',
            'contact_phone': '+7 (495) 123-45-67',
            'contact_person': 'Оргкомитет',
            'website': 'https://elibrary.ru',
            'is_featured': True,
            'is_free': False,
            'topics': ['Информатика', 'Искусственный интеллект', 'Цифровизация', 'Образование'],
        },

        # 3. Люминесценция (ФТИ им. Иоффе)
        {
            'title': 'Всероссийская конференция с международным участием по люминесценции',
            'organization': organizations.get('ФТИ им. Иоффе'),
            'conference_type': 'national',
            'format': 'offline',
            'start_date': date(2026, 5, 18),
            'end_date': date(2026, 5, 22),
            'deadline': date(2026, 3, 1),
            'location': 'Санкт-Петербург',
            'venue': 'ФТИ им. А.Ф. Иоффе / Академический университет',
            'address': 'Санкт-Петербург, Россия',
            'description': 'Всероссийская конференция с международным участием по люминесценции, организуемая ФТИ им. А.Ф. Иоффе и Академическим университетом им. Ж.И. Алфёрова. Посвящена фундаментальным и прикладным аспектам люминесценции, оптике и спектроскопии.',
            'program': 'Секции по фотолюминесценции, электролюминесценции, катодолюминесценции, люминесценции наноструктур и применению люминесцентных материалов.',
            'requirements': 'Тезисы принимаются до 1 марта 2026 г.',
            'participation_terms': 'Оргвзнос: 5000 руб., для студентов 2500 руб.',
            'contact_email': 'orekhova@mail.ioffe.ru',
            'contact_phone': '+7 (960) 243-92-38',
            'contact_person': 'Орехова Ксения Николаевна',
            'website': 'https://www.ioffe.ru/luminescence2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Физика', 'Физика полупроводников', 'Материаловедение'],
        },

        # 4. Dielectric and Ferroelectric Materials (ФТИ им. Иоффе)
        {
            'title': '6th Russia – China Workshop on Dielectric and Ferroelectric Materials',
            'organization': organizations.get('ФТИ им. Иоффе'),
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 9, 13),
            'end_date': date(2026, 9, 17),
            'deadline': date(2026, 6, 1),
            'location': 'Санкт-Петербург',
            'venue': 'ФТИ им. А.Ф. Иоффе',
            'address': 'Санкт-Петербург, Россия',
            'description': '6-й Российско-Китайский воркшоп по диэлектрическим и сегнетоэлектрическим материалам. Мероприятие объединяет ведущих учёных России и Китая для обсуждения последних достижений в области физики диэлектриков, сегнетоэлектриков и родственных материалов.',
            'program': 'Пленарные доклады, секционные заседания, постерная сессия.',
            'requirements': 'Тезисы принимаются до 1 июня 2026 г.',
            'participation_terms': 'Оргвзнос: 6000 руб.',
            'contact_email': 'koroleva@mail.ioffe.ru',
            'contact_phone': '+7 (812) 292-73-77',
            'contact_person': 'Королева Е.Ю.',
            'website': 'https://www.ioffe.ru/dielec2026',
            'is_featured': False,
            'is_free': False,
            'topics': ['Сегнетоэлектрики', 'Физика', 'Материаловедение'],
        },

        # 5. Шаг в будущее 2026 (МГТУ им. Баумана)
        {
            'title': 'Всероссийский форум научной молодёжи «Шаг в будущее» 2026',
            'organization': organizations.get('МГТУ им. Баумана'),
            'conference_type': 'national',
            'format': 'offline',
            'start_date': date(2026, 3, 23),
            'end_date': date(2026, 3, 27),
            'deadline': date(2026, 1, 15),
            'location': 'Москва',
            'venue': '14 научных центров и 11 университетов',
            'address': 'Москва, Россия',
            'description': 'Крупнейшее мероприятие для молодых исследователей и школьников, объединяющее 52 научные секции по всем направлениям: от инженерных наук до социально-гуманитарных. Организаторы: МГТУ им. Баумана, Российское молодёжное политехническое общество, при участии ведущих институтов РАН.',
            'program': '52 секции по 4 симпозиумам: Инженерные науки, Естественные науки, Математика и ИТ, Социально-гуманитарные науки. Участники: школьники, студенты, молодые учёные.',
            'requirements': 'Подробные требования к работам на сайте форума.',
            'participation_terms': 'Участие бесплатное. Регистрация открыта на сайте форума.',
            'contact_email': 'info@step-into-the-future.ru',
            'contact_phone': '+7 (499) 263-65-05',
            'contact_person': 'Оргкомитет',
            'website': 'https://www.step-into-the-future.ru',
            'is_featured': True,
            'is_free': True,
            'topics': [
                'Технические науки', 'Физика', 'Химия', 'Биология',
                'Математика', 'Информатика', 'Гуманитарные науки',
                'Экономика', 'Образование'
            ],
        },

        # 6. International Cryptology Conference (международная, для разнообразия)
        {
            'title': '46th International Cryptology Conference (Crypto 2026)',
            'organization': organizations.get('ФТИ им. Иоффе'),
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 8, 17),
            'end_date': date(2026, 8, 20),
            'deadline': date(2026, 2, 15),
            'location': 'США, Санта-Барбара',
            'venue': 'University of California',
            'address': 'Santa Barbara, California, USA',
            'description': 'Ведущая международная конференция по криптологии, посвященная фундаментальным и прикладным аспектам криптографии. Рейтинг CORE A+.',
            'program': 'Пленарные доклады, секционные заседания по теории криптографии, криптоанализу, протоколам, реализации криптосистем.',
            'requirements': 'Требования на сайте конференции.',
            'participation_terms': 'Регистрация открыта на сайте.',
            'contact_email': 'info@crypto2026.org',
            'contact_phone': '',
            'contact_person': 'Программный комитет',
            'website': 'https://crypto.iacr.org/2026/',
            'is_featured': False,
            'is_free': False,
            'topics': ['Информатика', 'Математика', 'Искусственный интеллект'],
        },

        # 7. ECML-PKDD 2026 (международная по машинному обучению)
        {
            'title': 'European Conference on Machine Learning and Data Mining (ECML-PKDD 2026)',
            'organization': organizations.get('ФТИ им. Иоффе'),
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 9, 7),
            'end_date': date(2026, 9, 11),
            'deadline': date(2026, 3, 14),
            'location': 'Италия, Неаполь',
            'venue': 'Конференц-центр',
            'address': 'Naples, Italy',
            'description': 'Ведущая европейская конференция по машинному обучению и интеллектуальному анализу данных, рейтинг CORE A.',
            'program': 'Основная конференция, воркшопы, туториалы, соревнования по анализу данных.',
            'requirements': 'Дедлайн подачи работ: 14 марта 2026 г.',
            'participation_terms': 'Регистрация открыта на сайте.',
            'contact_email': 'info@ecmlpkdd2026.org',
            'contact_phone': '',
            'contact_person': 'Оргкомитет',
            'website': 'https://ecmlpkdd.org/2026/',
            'is_featured': False,
            'is_free': False,
            'topics': ['Информатика', 'Искусственный интеллект', 'Математика'],
        },

        # 8. SIGIR 2026 (международная по информационному поиску)
        {
            'title': '46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2026)',
            'organization': organizations.get('ФТИ им. Иоффе'),
            'conference_type': 'international',
            'format': 'offline',
            'start_date': date(2026, 7, 15),
            'end_date': date(2026, 7, 19),
            'deadline': date(2026, 1, 22),
            'location': 'США',
            'venue': 'TBD',
            'address': 'USA',
            'description': 'Ведущая международная конференция по информационному поиску, рейтинг CORE A*.',
            'program': 'Пленарные доклады, секции по поиску информации, рекомендательным системам, NLP.',
            'requirements': 'Дедлайн подачи работ прошёл 22 января 2026 г.',
            'participation_terms': 'Регистрация открыта на сайте.',
            'contact_email': 'info@sigir2026.org',
            'contact_phone': '',
            'contact_person': 'Оргкомитет',
            'website': 'https://sigir2026.org/',
            'is_featured': False,
            'is_free': False,
            'topics': ['Информатика', 'Искусственный интеллект'],
        },

        # 9. Криосфера и Арктические исследования (дополнительно к существующим)
        {
            'title': 'Международная конференция «Криосфера и Арктические исследования: новые вызовы и технологии»',
            'organization': organizations.get('МГУ'),
            'conference_type': 'international',
            'format': 'hybrid',
            'start_date': date(2026, 11, 15),
            'end_date': date(2026, 11, 18),
            'deadline': date(2026, 9, 1),
            'location': 'Москва / онлайн',
            'venue': 'МГУ, Географический факультет',
            'address': 'Москва, Ленинские горы, д. 1',
            'description': 'Конференция, посвящённая исследованиям криосферы, Арктического региона, изменению климата и современным технологиям мониторинга.',
            'program': 'Секции по гляциологии, мерзлотоведению, полярным исследованиям, дистанционному зондированию.',
            'requirements': 'Тезисы принимаются до 1 сентября 2026 г.',
            'participation_terms': 'Участие бесплатное, онлайн-участие возможно.',
            'contact_email': 'cryo@geogr.msu.ru',
            'contact_phone': '+7 (495) 939-10-00',
            'contact_person': 'Оргкомитет',
            'website': 'https://www.geogr.msu.ru/cryo2026',
            'is_featured': True,
            'is_free': True,
            'topics': ['Криосфера', 'Арктические исследования', 'География', 'Науки о Земле'],
        },

        # 10. Энергетика будущего (ОИВТ РАН + МЭИ)
        {
            'title': 'Всероссийская конференция «Энергетика будущего: новые технологии и устойчивое развитие»',
            'organization': organizations.get('ОИВТ РАН'),
            'conference_type': 'national',
            'format': 'hybrid',
            'start_date': date(2026, 10, 20),
            'end_date': date(2026, 10, 23),
            'deadline': date(2026, 8, 1),
            'location': 'Москва',
            'venue': 'ОИВТ РАН / НИУ МЭИ',
            'address': 'Москва, Россия',
            'description': 'Конференция по новым технологиям в энергетике, возобновляемым источникам энергии, водородной энергетике и устойчивому развитию.',
            'program': 'Секции по возобновляемой энергетике, водородным технологиям, энергоэффективности, тепловой энергетике.',
            'requirements': 'Тезисы принимаются до 1 августа 2026 г.',
            'participation_terms': 'Оргвзнос: 6000 руб.',
            'contact_email': 'energy@jiht.ru',
            'contact_phone': '+7 (495) 484-23-33',
            'contact_person': 'Оргкомитет',
            'website': 'https://jiht.ru/energy2026',
            'is_featured': True,
            'is_free': False,
            'topics': ['Энергетика', 'Возобновляемая энергетика', 'Технические науки'],
        },
    ]

    conferences = []
    for conf_data in new_conferences_data:
        # Проверяем организацию
        if not conf_data['organization']:
            print_warning(f"Пропущена конференция '{conf_data['title'][:30]}...' - организация не найдена")
            continue

        topics_list = conf_data.pop('topics', [])

        # Устанавливаем статус
        if conf_data['end_date'] < today:
            conf_data['status'] = Conference.Status.ARCHIVED
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
        if 'participation_terms' not in conf_data:
            conf_data['participation_terms'] = ''
        if 'contact_phone' not in conf_data:
            conf_data['contact_phone'] = ''
        if 'contact_person' not in conf_data:
            conf_data['contact_person'] = ''
        if 'website' not in conf_data:
            conf_data['website'] = ''
        if 'is_featured' not in conf_data:
            conf_data['is_featured'] = False
        if 'is_free' not in conf_data:
            conf_data['is_free'] = True

        conf, created = Conference.objects.get_or_create(
            title=conf_data['title'],
            organization=conf_data['organization'],
            defaults=conf_data
        )

        if created:
            # Добавляем тематики
            for topic_name in topics_list:
                if topic_name in topics:
                    conf.topics.add(topics[topic_name])
            conf.save()
            print_success(f"Создана конференция: {conf.title[:50]}... ({conf.organization.short_name})")
            conferences.append(conf)
        else:
            print_info(f"Конференция уже существует: {conf.title[:40]}...")

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
            'affiliation': 'МФТИ, Физтех-школа физики и исследований им. Ландау',
            'academic_degree': 'student',
        },
        {
            'username': 'kozlov_asp',
            'email': 'dmitry.kozlov@phd.ru',
            'password': 'Aspirant2025!',
            'first_name': 'Дмитрий',
            'last_name': 'Козлов',
            'middle_name': 'Петрович',
            'affiliation': 'НИЯУ МИФИ, Институт ядерной физики и технологий',
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
    print_header("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ ТЕСТОВЫМИ ДАННЫМИ")
    print_info("Начинаем создание тестовых данных...")

    # Создаем тематики
    topics = create_topics()

    # Проверяем тематики
    check_topic_slugs()

    # Создаем основные организации
    organizations = create_organizations_and_users()

    # Добавляем новые организации
    new_orgs = create_additional_organizations()

    # Объединяем словари организаций
    organizations.update(new_orgs)

    # Создаем основные конференции
    conferences = create_conferences(organizations, topics)

    # Добавляем новые конференции
    new_conferences = create_additional_conferences(organizations, topics)

    # Создаем дополнительных участников
    create_additional_users()

    print_header("ИТОГИ ЗАПОЛНЕНИЯ")
    print_success(f"Всего тематик: {Topic.objects.count()}")
    print_success(f"Всего организаций: {Organization.objects.filter(is_active=True).count()}")
    print_success(f"Всего конференций: {Conference.objects.count()}")
    print_success(f"Всего пользователей: {CustomUser.objects.count()}")
    print_info(f"Из них организаций-пользователей: {Organization.objects.filter(is_active=True).count()}")
    print_info(
        f"Из них обычных участников: {CustomUser.objects.filter(is_superuser=False, organization__isnull=True).count()}")


if __name__ == '__main__':
    main()
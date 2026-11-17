# VetClinic — система учета ветеринарных посещений

Приложение для учета животных, ветеринарных врачей и их посещений.
Консольная версия (ПР3) дополнена веб-интерфейсом на Django (ПР5), HTML-страницы
переведены на систему шаблонов Django (ПР6), данные перенесены из JSON
в реляционную базу SQLite (ПР7), слой данных переведён на Django ORM
(ПР9), настроена административная панель и расширены возможности ORM
(ПР10), добавлены формы Django и загрузка изображений (ПР11).

## Начало
Приложение позволяет:
* просматривать и искать животных;
* просматривать и искать врачей;
* проверять доступность врача на дату;
* создавать и отменять посещения;
* просматривать список посещений;
* добавлять назначения (лечение) к посещению.

## Целевая аудитория
Администраторы и врачи ветеринарной клиники, которым нужно вести учет
животных, врачей, посещений и назначенного лечения.

## Предметная область
Основными объектами предметной области являются: животное, врач,
посещение и назначение (входит в состав посещения). Пользователь
записывает животное на посещение к врачу на определенную дату. Один
врач не может иметь два активных посещения на одну и ту же дату.
Отмененное посещение не блокирует врача и позволяет создать новое
посещение на ту же дату.

## Основные сущности

### Animal — животное
Объект `Animal` представляет животное, состоящее на учете в клинике.

Основные атрибуты:
* `id` — уникальный идентификатор;
* `name` — кличка;
* `species` — вид;
* `age` — возраст;
* `owner` — владелец.

Основные методы:
* `is_species()` — проверка принадлежности к виду;
* `__str__()` — строковое представление животного.

### Doctor — врач
Объект `Doctor` представляет ветеринарного врача клиники.

Основные атрибуты:
* `id` — уникальный идентификатор;
* `name` — ФИО врача;
* `specialization` — специализация.

Основные методы:
* `__str__()` — строковое представление врача;
* `from_data()` — создание объекта из данных JSON.

### Visit — посещение
Объект `Visit` представляет посещение клиники животным.

Основные атрибуты:
* `id` — уникальный идентификатор посещения;
* `animal` — объект `Animal`;
* `doctor` — объект `Doctor`;
* `visit_date` — дата посещения;
* `diagnosis` — диагноз;
* `is_cancelled` — признак отмены посещения;
* `prescriptions` — список объектов `Prescription`.

Основные методы:
* `cancel()` — отмена посещения;
* `set_diagnosis()` — установка диагноза;
* `add_prescription()` — добавление назначения;
* `__str__()` — строковое представление посещения с учетом статуса.

### Prescription — назначение
Объект `Prescription` представляет назначенное животному лечение в
рамках посещения.

Основные атрибуты:
* `medication` — препарат;
* `dosage` — дозировка;
* `duration` — длительность приема.

Основные методы:
* `__str__()` — строковое представление назначения.

## Основные операции

### Работа с животными
* добавление животного;
* поиск животного по кличке;
* фильтрация животных по виду;
* сортировка животных по возрасту;
* просмотр списка животных.

### Работа с врачами
* создание врача;
* поиск врача;
* просмотр информации о враче.

### Работа с посещениями
* создание посещения;
* проверка доступности врача;
* отмена посещения;
* добавление диагноза и назначения;
* просмотр списка посещений.

При создании посещения проверяется наличие другого активного посещения
этого же врача на ту же дату.

## Хранение данных
Данные приложения хранятся в файлах:
* `data/animals.json`;
* `data/doctors.json`;
* `data/visits.json`.

При загрузке данные из JSON преобразуются в объекты `Animal`, `Doctor` и
`Visit`. При сохранении объекты преобразуются обратно в данные JSON. Для
связи посещения с животным и врачом в `visits.json` используются их
идентификаторы `animal_id` и `doctor_id`.

Начиная с ПР7 веб-приложение читает данные из базы SQLite
`data/vetclinic.sqlite` (см. раздел «Слой базы данных»), а JSON-файлы
используются консольной версией и как источник для импорта.

## Структура проекта
```
vet_clinic/
│
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
├── storage.py
├── utils.py
│
├── models/
│   ├── __init__.py
│   ├── animals.py
│   ├── doctors.py
│   └── visits.py
│
├── data/
│   ├── animals.json
│   ├── doctors.json
│   └── visits.json
│
└── tests/
    ├── test_animals.py
    ├── test_doctors.py
    └── test_visits.py
```

## Назначение модулей
### `main.py`
Точка входа в приложение. Отвечает за:
* запуск приложения;
* отображение меню;
* получение данных от пользователя;
* организацию пользовательских сценариев.

### `models/animals.py`
Содержит класс `Animal` и функции работы с животными.

### `models/doctors.py`
Содержит класс `Doctor` и функции работы с врачами.

### `models/visits.py`
Содержит классы `Visit`, `Prescription` и функции работы с посещениями.

### `storage.py`
Отвечает за загрузку и сохранение данных. Выполняет преобразование:
* JSON → объекты Python;
* объекты Python → JSON.

### `utils.py`
Содержит вспомогательные функции:
* `input_int()` — безопасный ввод целого числа;
* `input_date()` — безопасный ввод даты.

### `tests/`
Содержит автоматизированные тесты проекта.

## Запуск приложения
Для запуска приложения выполнить:
```
python main.py
```

## Тестирование
Для запуска автоматизированных тестов выполнить:
```
pytest -v
```

Тесты проверяют:
* создание и работу объектов `Animal`, `Doctor` и `Visit`;
* методы классов;
* операции с животными;
* создание и отмену посещений;
* связь посещения с животным и врачом;
* правило доступности врача на дату.

## Проверка качества кода
Для проверки соответствия кода требованиям PEP 8 используется `flake8`:
```
flake8 .
```

## Git
Исходный код проекта хранится в Git-репозитории.
Для проверки состояния репозитория:
```
git status
```

## Планы развития
* подключение базы данных к Django через ORM;
* разработка API;
* реализация пользователей и авторизации;
* контейнеризация приложения;
* настройка CI/CD.

## Веб-интерфейс на Django (ПР5–ПР6)

### Используемые технологии
* Python 3, Django 5.2 (LTS) — веб-фреймворк;
* Django Template Language — шаблоны (`extends`, `block`, `include`,
  `for`, `if`, `url`, `static`, фильтры);
* HTML, Bootstrap 5.3 (CDN) и собственные CSS и JavaScript;
* pytest, flake8 — тесты и проверка стиля.

### Страницы и URL
| URL | Имя маршрута | View | Шаблон |
|---|---|---|---|
| `/` | `homepage:index` | `index()` | `homepage/index.html` |
| `/animals/` | `animals:list` | `animals()` | `animals/animal_list.html` |
| `/animals/<slug:slug>/` | `animals:detail` | `animal_detail()` | `animals/animal_detail.html` |
| `/animals/create/` | `animals:create` | `animal_create()` | `animals/animal_form.html` |
| `/doctors/` | `doctors:list` | `doctors()` | `doctors/doctor_list.html` |
| `/visits/` | `visits:list` | `visits()` | `visits/visit_list.html` |
| `/visits/active/` | `visits:active` | `active_visits()` | `visits/visit_list.html` |
| `/visits/available/` | `visits:available` | `available_doctors()` | `visits/available.html` |
| `/visits/statistics/` | `visits:statistics` | `statistics()` | `visits/statistics.html` |
| `/visits/<int:visit_id>/` | `visits:detail` | `visit_detail()` | `visits/visit_detail.html` |
| `/visits/create/` | `visits:create` | `visit_create()` | `visits/visit_form.html` |
| `/visits/<int:visit_id>/edit/` | `visits:update` | `visit_update()` | `visits/visit_form.html` |
| `/visits/<int:visit_id>/cancel/` | `visits:cancel` | `visit_cancel()` (только POST) | — |
| `/admin/` | — | панель администратора Django (ПР10) | — |

Если животное или посещение не найдено, `get_object_or_404()` возвращает
ответ 404 (ПР9); оформляет его `handler404`
(`homepage.views.page_not_found()`, шаблон `404.html`).

### Как устроены шаблоны (ПР6)
View-функция только загружает данные средствами ПР3, формирует контекст
и вызывает `render(request, "шаблон", context)`. HTML в Python не
формируется, функция `page()` из ПР5 удалена.

* `templates/base.html` — общий каркас: `{% block title %}`,
  `{% block content %}`, Bootstrap, собственный CSS, логотип, подвал,
  JavaScript;
* `templates/includes/navigation.html` — навигация, ссылки через
  `{% url %}`;
* `templates/404.html` — страница ошибки 404;
* `homepage/templates/homepage/index.html` — главная;
* `animals/templates/animals/` — `animal_list.html`, `animal_detail.html`,
  `includes/animal_card.html` (карточка одного животного);
* `visits/templates/visits/` — `visit_list.html`, `visit_detail.html`,
  `includes/visit_status.html` (статус, используется в списке посещений,
  на странице посещения и в истории животного).

Используются: наследование шаблонов, блоки, включаемые шаблоны,
циклы `{% for %}` с `{% empty %}`, условия `{% if %}`, именованные
маршруты с пространствами имён (`app_name`), фильтры `length` и
`default`.

### Статические файлы
Лежат в `homepage/static/homepage/` и подключаются через
`{% load static %}` и `{% static %}` в `base.html`:
* `css/style.css` — собственные стили (карточки, статусы, логотип);
* `js/main.js` — подставляет текущий год в подвал;
* `img/logo.png` — логотип.

### Структура проекта
```text
vet_clinic/
├── manage.py
├── requirements.txt
├── pytest.ini
├── .flake8
├── main.py            # консольная версия (ПР3)
├── storage.py         # JSON-хранилище
├── utils.py
├── vetclinic/         # настройки Django-проекта
├── templates/         # base.html, includes/, 404.html
├── homepage/          # главная страница, static/
├── animals/           # страницы животных
├── doctors/           # страница врачей (ПР7)
├── visits/            # страницы посещений, поиск врача, статистика
├── db/                # слой SQLite (ПР7) и перенос данных в ORM (ПР9)
├── sql/               # schema.sql и queries.sql (ПР7)
├── models/            # классы предметной области (ПР3)
├── data/              # JSON-файлы и база vetclinic.sqlite
└── tests/             # тесты pytest
```

### Запуск
```text
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python -m db.import_sqlite_to_orm   # перенос данных из data/vetclinic.sqlite
python manage.py createsuperuser    # для входа в /admin/
python manage.py check
python manage.py runserver
```
Затем открыть http://127.0.0.1:8000/. Консольная версия: `python main.py`.
Готовая база `data/vetclinic.sqlite` уже лежит в репозитории; при
необходимости её можно создать заново (см. раздел «Слой базы данных»).
Проверка статики: `python manage.py findstatic homepage/img/logo.png`.

### Тесты и проверка кода
```text
pytest -v
flake8 . --extend-exclude=venv
```
Тесты Django работают через `pytest-django` с отдельной тестовой базой
и не меняют `db.sqlite3` и `data/`.

## Слой базы данных (ПР7)

### Текущий этап разработки
На ПР7 данные VetClinic перенесены из JSON в базу данных SQLite:
* создана база данных `data/vetclinic.sqlite`;
* таблицы созданы с помощью `sql/schema.sql`;
* данные перенесены из JSON скриптом `db/import_json.py`;
* SQL-запросы (22 шт.) сохранены в `sql/queries.sql`;
* Django-представления получают данные из SQLite через модуль `sqlite3`;
* страницы животных, врачей, посещений, поиска свободного врача и
  статистики работают с базой данных.

Путь данных: `SQLite → SQL → sqlite3 → Django view → context → шаблон
→ страница`. В ПР9 представления переведены на Django ORM; слой `db/` и
`sql/` сохранён как источник данных и справочный материал ПР7.
JSON-файлы и консольная версия (`main.py`, `storage.py`, `models/`)
сохранены как предыдущая реализация и источник данных для импорта.

### Структура базы данных
**animals** — животные

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER, PRIMARY KEY | идентификатор |
| `name` | TEXT, NOT NULL | кличка |
| `species` | TEXT, NOT NULL | вид |
| `age` | INTEGER, NOT NULL, `>= 0` | возраст |
| `owner` | TEXT, NOT NULL | владелец |

**doctors** — врачи

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER, PRIMARY KEY | идентификатор |
| `name` | TEXT, NOT NULL | ФИО |
| `specialization` | TEXT, NOT NULL | специализация |

**visits** — посещения

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER, PRIMARY KEY | идентификатор |
| `animal_id` | INTEGER, NOT NULL, FOREIGN KEY | ссылка на `animals.id` |
| `doctor_id` | INTEGER, NOT NULL, FOREIGN KEY | ссылка на `doctors.id` |
| `visit_date` | TEXT, NOT NULL | дата в формате `YYYY-MM-DD` |
| `diagnosis` | TEXT, NULL допустим | диагноз (до приёма отсутствует) |
| `is_cancelled` | INTEGER, NOT NULL, по умолчанию 0 | 0 — активно, 1 — отменено |

**prescriptions** — назначения

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER, PRIMARY KEY AUTOINCREMENT | идентификатор |
| `visit_id` | INTEGER, NOT NULL, FOREIGN KEY | ссылка на `visits.id` (каскадное удаление) |
| `medication` | TEXT, NOT NULL | препарат |
| `dosage` | TEXT, NOT NULL | дозировка |
| `duration` | TEXT, NOT NULL | длительность приёма |

Связи: одно животное — много посещений, один врач — много посещений,
одно посещение — много назначений. Первичные ключи — поля `id`,
внешние ключи — `visits.animal_id`, `visits.doctor_id`,
`prescriptions.visit_id`. Проверка внешних ключей включается при каждом
подключении командой `PRAGMA foreign_keys = ON` (`db/database.py`).

### Файлы
* `sql/schema.sql` — создание таблиц и индексов (`IF NOT EXISTS`);
* `sql/queries.sql` — SQL-запросы проекта с комментариями;
* `db/database.py` — подключение к SQLite, `init_db()`, `create_database()`;
* `db/import_json.py` — перенос данных из JSON (`executemany()`,
  параметры `?`, `commit()` / `rollback()`);
* `data/vetclinic.sqlite` — файл базы данных.

### Создание базы и импорт данных
Команды выполняются из корня проекта:
```text
python -m db.database          # создать файл базы и таблицы
python -m db.import_json       # перенести данные из JSON
python -m db.import_json --force   # очистить таблицы и импортировать заново
```
Проверка в SQLite CLI:
```text
sqlite3 data/vetclinic.sqlite
sqlite> .tables
sqlite> SELECT COUNT(*) FROM visits;
```
Запуск всех запросов файла: `sqlite3 data/vetclinic.sqlite < sql/queries.sql`.

### SQL-запросы (`sql/queries.sql`)
| № | Назначение | Вид |
|---|---|---|
| 1–2 | список животных, список врачей | выборка списков |
| 3 | виды животных без повторов | `DISTINCT` |
| 4 | ближайшие посещения | `ORDER BY`, `LIMIT`, `OFFSET` |
| 5–7 | животные по виду, поиск по кличке, по возрасту | `WHERE`, `LIKE`, `IN` |
| 8–10 | активные посещения, за период, без диагноза | `WHERE`, `BETWEEN`, `IS NULL` |
| 11 | свободные врачи на дату | подзапрос `NOT IN` |
| 12–14 | посещения с животным и врачом, история животного, назначения | `JOIN` |
| 15–17 | число активных посещений, возраст, занятость врача | `COUNT`, `AVG`, `MIN`, `MAX` |
| 18–19 | животные по видам, посещения по врачам | `GROUP BY`, `LEFT JOIN` |
| 20–21 | виды и врачи с порогом | `GROUP BY` + `HAVING` |
| 22 | самые назначаемые препараты | `GROUP BY`, `LIMIT` |

### Как данные попадают на страницы
View получает соединение (`get_connection()` +
`conn.row_factory = sqlite3.Row`), выполняет запрос с параметрами `?`,
передаёт результат в шаблон через `context`; в шаблоне поля доступны по
именам (`{{ visit.animal_name }}`). Значения из адресной строки никогда
не подставляются в текст SQL — только параметрами.

| Страница | Что показывает | Запросы |
|---|---|---|
| `/animals/` | список, поиск `?q=`, фильтр `?species=` | 1, 3, 5, 6 |
| `/animals/<id>/` | животное и история посещений | 13 |
| `/doctors/` | врачи и их активные посещения, фильтр `?spec=` | 2, 19 |
| `/visits/` | все посещения | 12 |
| `/visits/active/` | активные посещения | 8, 12 |
| `/visits/<id>/` | посещение, назначения, занятость врача сегодня | 12, 17 |
| `/visits/available/?date=` | свободные врачи на дату | 11 |
| `/visits/statistics/?min=` | сводные показатели | 15, 16, 18, 19, 21, 22 |

Для регистронезависимого поиска по кириллице в соединении
зарегистрирована функция `py_lower()` (встроенный `LOWER()` SQLite
работает только с латиницей). Служебная база Django `db.sqlite3`
(`DATABASES`) хранится отдельно и данными проекта не используется.

## Django ORM (ПР9)

Слой данных переведён с `sqlite3` и ручных SQL-запросов на модели Django.
Выбрана стратегия «таблицы управляются Django + перенос данных»:
исходная база `data/vetclinic.sqlite` (ПР7) не меняется и служит
источником, а Django работает с `db.sqlite3` (`DATABASES`), таблицы в
которой создают миграции.

### Модели и связи
| Модель | Файл | Поля |
|---|---|---|
| `Animal` | `animals/models.py` | `name`, `species`, `age`, `owner`, `photo`, `slug`, `is_senior` |
| `Doctor` | `doctors/models.py` | `name`, `specialization` |
| `Visit` | `visits/models.py` | `animal` (FK), `doctor` (FK), `visit_date`, `diagnosis`, `status` |
| `Prescription` | `visits/models.py` | `visit` (FK, CASCADE), `medication`, `dosage`, `duration` |

Внешние ключи `Visit.animal` и `Visit.doctor` используют
`on_delete=PROTECT` (история посещений не теряется) и
`related_name="visits"`; `Prescription.visit` — `CASCADE`, как в схеме
ПР7 (`animal.visits.all()`, `doctor.visits.all()`,
`visit.prescriptions.all()`).

### Миграции и перенос данных
```text
python manage.py migrate
python -m db.inspect_source_db      # структура исходной базы (только чтение)
python -m db.import_sqlite_to_orm   # перенос с сохранением id и связей
python manage.py showmigrations
```
`db/import_sqlite_to_orm.py` переносит животных, врачей, посещения и
назначения одной транзакцией (`transaction.atomic()`,
`update_or_create(pk=...)`), поэтому повторный запуск безопасен.
Даты `YYYY-MM-DD` превращаются в `date`, `is_cancelled` — в `status`.

### ORM-запросы в проекте
| Направление | Запрос | Где |
|---|---|---|
| Получение | `Animal.objects.all()`; `get_object_or_404(Animal, slug=...)`; `get_object_or_404(Visit.objects.select_related(...), pk=...)` | `animals/views.py`, `visits/views.py` |
| Фильтрация | `filter(species=...)`; цепочка `for_date()` + `filter(animal=...)` + `filter(doctor=...)`; по связанному полю `filter(doctor__specialization=...)`; `exclude(pk__in=...)` | `animals`, `visits` |
| Поиск | `PyLower` + `contains` по кличке; `Q(name) \| Q(owner)`; поиск врача по ФИО или специализации | `animals`, `doctors` |
| Сортировка | `order_by("visit_date", "id")`; `order_by("animal__name")`; `order_by("-visits_count")` | `visits/views.py` |
| Связи | `select_related("animal", "doctor")`; `animal.visits.select_related("doctor")`; `annotate(F("animal__name"))` + `values()` | `visits/views.py`, `animals/views.py` |
| Агрегация | `aggregate(Count, Avg, Min, Max)`; `annotate(Count(..., filter=Q(...)))`; `values().annotate(Count)`; `.count()` | `visits/views.py` |
| Страницы | `Paginator(..., 5)`, `get_page()`, `{% querystring %}` | `visits/views.py`, `visit_list.html` |

Параметр сортировки не передаётся в `order_by()` напрямую: используется
словарь `SORT_FIELDS`. Статистика по врачам строится от `Doctor`, поэтому
врачи без активных посещений остаются в результате со значением 0.

Регистронезависимый поиск по кириллице в SQLite: встроенные `LIKE` и
`LOWER()` работают только с латиницей, поэтому `vetclinic/sqlite_functions.py`
регистрирует функцию `py_lower()` при подключении (сигнал
`connection_created`) и даёт выражение `PyLower`.

## Административная панель и ORM (ПР10)

* **Admin** (`/admin/`, `createsuperuser`): модели `Animal`, `Doctor`,
  `Visit`, `Prescription` зарегистрированы через `@admin.register`.
  Русские названия приложений (`verbose_name` в `AppConfig`), моделей и
  полей; `list_display`, `list_display_links`, `search_fields`,
  `list_filter`, `ordering`, `list_per_page`, `list_editable`
  (возраст), `readonly_fields` (`id`, `slug`, `is_senior`),
  `date_hierarchy`, `autocomplete_fields`, `list_select_related`.
* **Inline**: посещения на страницах животного и врача, назначения на
  странице посещения.
* **Аннотации в списках**: число активных посещений считается одним
  запросом (`get_queryset()` + `Count(..., filter=Q(...))`).
* **Действия**: «Отменить», «Отметить завершёнными», «Вернуть в
  активные» (с проверкой занятости врача), «Увеличить возраст на 1 год»
  (`update(age=F("age") + 1)`).
* **Статус посещения** — `TextChoices` `Visit.Status` (`active`,
  `cancelled`, `completed`) вместо `is_cancelled`; миграции
  `visits/0002–0004` добавляют поле, переносят данные (`RunPython`) и
  удаляют старое поле. Блокирует врача только активное посещение.
* **Менеджер** `VisitManager` на основе `VisitQuerySet`:
  `Visit.objects.active() / cancelled() / completed() / for_date(d)`;
  `Visit.objects.all()` по-прежнему возвращает всю историю.
* **slug**: `/animals/barsik-1/` вместо `/animals/1/`. Транслитерация
  (`Unidecode`) + `slugify`; миграции `animals/0002–0004` добавляют поле,
  заполняют его для существующих животных и делают уникальным;
  `Animal.get_absolute_url()` даёт ссылку «Посмотреть на сайте» в админке.
* **GeneratedField** `Animal.is_senior` — вычисляется базой данных
  (возраст не менее 8 лет), в формы не входит.
* **Контекстный процессор** `animals.context_processors.clinic_context`
  передаёт `site_name` и `animals_count` во все шаблоны (`base.html`,
  навигация «Животные (N)»).
* **Django Debug Toolbar** подключается в `settings.py` автоматически, если
  пакет установлен и `DEBUG = True` (маршрут `/__debug__/`); при запуске
  тестов отключён.
* Правило «у врача одно активное посещение на дату» проверяет
  `Visit.clean()`, поэтому оно действует и в формах сайта, и в админке.

Права доступа: для проверки ограничений создайте в админке группу
(например, «Операторы клиники») с правами `view/add/change` для
животных и посещений без `delete`, а затем пользователя с `is_staff`
без `is_superuser`.

## Формы Django (ПР11)

* `visits/forms.py` → `VisitFilterForm` (`forms.Form`): фильтры списка
  посещений по дате, животному, врачу, специализации врача, статусу и
  сортировка. Форма читает `request.GET`; при ошибках показывается
  сообщение и фильтры не применяются. Пагинация, `F()`/`values()` и
  `Visit.objects.active()` сохранены.
* `VisitForm` (`ModelForm`): создание (`/visits/create/`) и
  редактирование (`/visits/<id>/edit/`) через `instance`. Статус в форму
  не входит, новое посещение всегда активно. `clean_visit_date()` не
  разрешает прошедшую дату (неизменённая дата у существующей записи
  допустима); занятость врача проверяет `Visit.clean()`.
* Отмена `/visits/<id>/cancel/` — только POST (`@require_POST`),
  вызывается `visit.cancel()`, запись не удаляется. Формы изменяют данные
  только с `{% csrf_token %}`.
* `animals/forms.py` → `AnimalForm`: создание животного с фотографией
  (`ImageField`, Pillow). `enctype="multipart/form-data"`, `request.FILES`;
  размер до 2 МБ, форматы JPEG/PNG/WEBP. Файлы хранятся в `media/animals/`
  (`MEDIA_ROOT`, `MEDIA_URL`), отдельно от статики; каталог `media/`
  добавлен в `.gitignore`.
* Общий шаблон `visits/visit_form.html` для создания и редактирования,
  ошибки полей и формы, подсказки `help_text`, сообщения `messages`.

## Проверка проекта (ПР9–ПР11)
```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
pytest -v
flake8 . --extend-exclude=venv
```
Тесты: модели и менеджер (`test_models.py`), формы и загрузка фото
(`test_forms.py`), страницы и ORM-запросы (`test_web.py`), список,
создание, редактирование и отмена (`test_visit_views.py`), админка
(`test_admin.py`), перенос данных (`test_transfer.py`), слой SQLite ПР7
(`test_database.py`).

## Текущее состояние и план развития
Реализовано: консольная версия (ПР3), Django-проект с маршрутизацией
(ПР5), шаблонный интерфейс со статикой (ПР6), SQLite и SQL-запросы
(ПР7), модели, миграции и ORM (ПР9), административная панель, менеджер,
статусы, slug, `GeneratedField`, контекстный процессор (ПР10), формы,
валидация и загрузка изображений (ПР11).

Планируется: аутентификация, добавление назначений через формы, API.

"""Настройки Django-проекта vetclinic (Django 5.2)."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ключ только для учебной разработки; в рабочей среде хранится отдельно.
SECRET_KEY = (
    "django-insecure-igkrw45azb7vdlsozuxlth15gjzrlwykr470yi9jhfsj250tao"
)

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "homepage.apps.HomepageConfig",
    "animals.apps.AnimalsConfig",
    "doctors.apps.DoctorsConfig",
    "visits.apps.VisitsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vetclinic.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # ПР10: название клиники и число животных во всех шаблонах.
                "animals.context_processors.clinic_context",
            ],
        },
    },
]

WSGI_APPLICATION = "vetclinic.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

# ПР11: загруженные пользователями файлы (фотографии животных) хранятся
# отдельно от статических ресурсов приложения.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ПР9: исходная база SQLite из ПР7 (sqlite3 без ORM). Используется только
# как источник данных для переноса: python -m db.import_sqlite_to_orm.
# Рабочая база приложения — db.sqlite3 (DATABASES выше), таблицы в ней
# создают миграции Django.
DB_PATH = BASE_DIR / "data" / "vetclinic.sqlite"

# JSON-файлы данных из ПР3 (консольная версия и источник для импорта).
DATA_DIR = BASE_DIR / "data"
ANIMALS_FILE = str(DATA_DIR / "animals.json")
DOCTORS_FILE = str(DATA_DIR / "doctors.json")
VISITS_FILE = str(DATA_DIR / "visits.json")

# ПР10: Django Debug Toolbar подключается только в режиме разработки,
# если пакет установлен, и не мешает тестам.
RUNNING_TESTS = "pytest" in sys.modules or "test" in sys.argv

try:
    import debug_toolbar  # noqa: F401
except ImportError:
    debug_toolbar = None

if DEBUG and debug_toolbar is not None and not RUNNING_TESTS:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(
        1, "debug_toolbar.middleware.DebugToolbarMiddleware"
    )
    INTERNAL_IPS = ["127.0.0.1"]

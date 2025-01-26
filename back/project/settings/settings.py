import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)

ENV_NAME = "dev"

SITE_ID = 1

SECRET_KEY = "FAKE_vvvvvaaaa"

INTERNAL_IPS = [
    "0.0.0.0",
    "127.0.0.1",
]

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
]

ADMINS = [
    "gregory@stopdesign.ru",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_DIR, "db/db.sqlite3"),
        "ATOMIC_REQUESTS": True,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 10,
        "OPTIONS": {
            "timeout": 10,
        },
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.sessions",
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "constance",
    "constance.backends.database",
    "project",
    "main",
]


# своя модель для пользователей
AUTH_USER_MODEL = "main.User"


# кроны
CRON_CLASSES = [
    # 'main.cron.CurrenciesUpdateFiat',
]
DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 30
FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Server check]: "


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "project.urls"

TEMPLATES = [
    # Стардартные шаблоны Django для админки и чужих приложений
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "project/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "project.context_processors.each_context",
            ],
        },
    },
]

# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
#
# STATICFILES_FINDERS = [
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# ]

# STATICFILES_DIRS = []

MEDIA_ROOT = os.path.join(ROOT_DIR, "www/media")
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(ROOT_DIR, "www/static")
STATIC_URL = "/static/"


FIXTURE_DIRS = [BASE_DIR]

WSGI_APPLICATION = "project.wsgi.application"


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Argon2 is the winner of the 2015 Password Hashing Competition,
# a community organized open competition to select a next generation hashing algorithm.
PASSWORD_HASHERS = [
    # 'django.contrib.auth.hashers.Argon2PasswordHasher',
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]


# CSRF_USE_SESSIONS = False
# CSRF_COOKIE_NAME = 'a_csrf'
# CSRF_COOKIE_PATH = '/admin/'
# CSRF_COOKIE_HTTPONLY ???
# CSRF_COOKIE_SECURE = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # 'DEFAULT_PARSER_CLASSES': (
    #     'main.drf.CustomJSONParser',
    # ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'main.drf.CustomJSONRenderer',  # чтобы сериалайзить Money и всякое такое
    # ),
    # 'EXCEPTION_HANDLER': 'main.drf.full_details_exception_handler',
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 1000,
}


APPEND_SLASH = False

TIME_ZONE = "Europe/Moscow"

USE_I18N = False
USE_L10N = False
USE_TZ = True


DATE_FORMAT = "d.m.Y"
SHORT_DATE_FORMAT = "d.m.Y"
DATETIME_FORMAT = "d.m.Y, H:i:s"
SHORT_DATETIME_FORMAT = "d.m.Y, H:i"

TIME_FORMAT = "H:i:s"
SHORT_TIME_FORMAT = "H:i"


DEFAULT_FILE_STORAGE = "project.helpers.services.ASCIIFileSystemStorage"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "Admin <noreply@stopdesign.ru>"

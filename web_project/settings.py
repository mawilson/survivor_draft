"""
Django settings for web_project project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
is_prod = str(os.getenv("DJANGO_SURVIVOR_PROD"))
DEBUG = (
    is_prod != "true"
)  # if the env var is undefined, debug will be set to True - only if the env var is present & 'true' will debug be set to False

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = os.getenv("SECRET_KEY_DEV")
else:
    SECRET_KEY = os.getenv("SECRET_KEY")
if (
    SECRET_KEY is None
):  # if the appropriate environment variable for secret key was not present, generate a new one
    SECRET_KEY = (
        get_random_secret_key()
    )  # if environment has not provided a secret key, generate a random one for this server runtime
else:
    SECRET_KEY = str(SECRET_KEY)

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["outdraft.me"]

if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

# Application definition

INSTALLED_APPS = [
    "daphne",
    "survive",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "debug_toolbar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "web_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "web_project.wsgi.application"
ASGI_APPLICATION = "web_project.asgi.application"

if DEBUG:
    channel_layers_config = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"  # for dev use only!!
        }
    }
else:
    channel_layers_config = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {  # type: ignore[dict-item]
                "hosts": [
                    ("redis", 6379)
                ],  # this assumes a network named 'redis' will be available at port 6379, which will be true if running thru docker compose
            },
        }
    }
CHANNEL_LAYERS = channel_layers_config

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db/db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "static_collected"

MEDIA_URL = "media/"
MEDIA_ROOT = [BASE_DIR / "media"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/profile"  # on login, redirect to profile page

if not DEBUG:  # Security/HTTPS settings to be set when not in development mode
    SECURE_SSL_REDIRECT = True  # redirect all non-HTTPS requests to HTTPS
    SESSION_COOKIE_SECURE = True  # generate secure cookies
    CSRF_COOKIE_SECURE = True  # sessions will not work over HTTP, & POST data will not be sent over HTTP - should be fine given SECURE_SSL_REDIRECT to HTTPS
    SECURE_HSTS_SECONDS = 3600  # small value temporary, later 31536000 (one year).

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # while email does not work, just do console backend
email_enabled = os.getenv("DJANGO_SURVIVOR_EMAIL_ENABLED") == "true"
if DEBUG or not email_enabled:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_BACKEND = "survive.backends.email.EmailBackend"
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 10
    EMAIL_HOST = str(os.getenv("DJANGO_SURVIVOR_EMAIL_HOST"))
    port = os.getenv("DJANGO_SURVIVOR_EMAIL_PORT") or ""
    try:
        port_int = int(port)
        if (
            port_int < 0 or port_int > 65535
        ):  # valid ports are between 0 & 65535 inclusive
            raise ValueError
        EMAIL_PORT = port_int
    except ValueError:
        print(
            f"Configured email port of '{port}' was not a valid port, will use default port value."
        )
    EMAIL_HOST_USER = str(os.getenv("DJANGO_SURVIVOR_EMAIL_USER"))
    EMAIL_HOST_PASSWORD = str(os.getenv("DJANGO_SURVIVOR_EMAIL_PASSWORD"))
    EMAIL_SSL_KEYFILE = str(os.getenv("DJANGO_SURVIVOR_EMAIL_KEYFILE"))
    EMAIL_SSL_CERTFILE = str(os.getenv("DJANGO_SURVIVOR_EMAIL_CERTFILE"))
DEFAULT_FROM_EMAIL = "jeffbot@outdraft.me"

"""
Django settings for supplierIntegration project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from datetime import timedelta
from email.utils import parseaddr

import environ
import os
from pathlib import Path

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

MAIN_APPS = [
    'main.apps.MainConfig',
    'report.apps.ReportConfig',
    'supplier.apps.SupplierConfig',


]

CONNECTOR_APPS = [
    'onec_connector.apps.OnecConnectorConfig',
    'yml_connector.apps.YmlConnectorConfig',
    'api_connector.apps.ApiConnectorConfig',
    'excel_connector.apps.ExcelConnectorConfig',
    'scrapy_connector.apps.ScrapyConnectorConfig',
    'gpt_connector.apps.GptConnectorConfig',
    'telegram_connector.apps.TelegramConnectorConfig',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS += MAIN_APPS
INSTALLED_APPS += CONNECTOR_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'supplierIntegration.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Media file support
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'supplierIntegration.wsgi.application'
ASGI_APPLICATION = "supplierIntegration.asgi.application"


# Channels
# https://channels.readthedocs.io/en/latest/

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'service': 'integration',
            'passfile': '.pgpass',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    BASE_DIR / 'storage',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = 'media/'

MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework
# https://docs.djangoproject.com/en/5.0/ref/contrib/sites/

SITE_ID = 1

# Django Superuser
# https://docs.djangoproject.com/en/4.2/ref/django-admin/#createsuperuser

DJANGO_SUPERUSER_PASSWORD = env('DJANGO_SUPERUSER_PASSWORD')

DJANGO_SUPERUSER_EMAIL = env('DJANGO_SUPERUSER_EMAIL')

DJANGO_SUPERUSER_USERNAME = env('DJANGO_SUPERUSER_USERNAME')

# SMTP
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-EMAIL_BACKEND

SERVER_EMAIL = env('SERVER_EMAIL')

DEFAULT_FROM_EMAIL = env('SERVER_EMAIL')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = env('EMAIL_HOST')

EMAIL_HOST_USER = DEFAULT_FROM_EMAIL

EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

EMAIL_PORT = env('EMAIL_PORT')

EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX')

EMAIL_USE_TLS = False

EMAIL_USE_SSL = True

# Auth
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-user-model

#AUTH_USER_MODEL = 'account.Account'

ADMINS = tuple(parseaddr(email) for email in env.list('ADMINS'))

MANAGERS = tuple(parseaddr(email) for email in env.list('MANAGERS'))


# Logging
# https://docs.djangoproject.com/en/4.2/howto/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'WARNING',
            'include_html': True,
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
            'filters': [],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}


# Celery
# https://docs.celeryq.dev/en/stable/

CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

CELERY_CACHE_BACKEND = 'amqp://developer:integration@rabbitmq:5672/'

CELERY_TIMEZONE = TIME_ZONE

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = 30 * 60

# Cross-origin resource sharing
# https://github.com/adamchainz/django-cors-headers

CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://ws.localhost",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost",
    "http://ws.localhost",
]

CSRF_COOKIE_HTTPONLY = True

CSRF_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_SAMESITE = "Lax"

# Additional
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
import os
from pathlib import Path

from decouple import Csv, config

DEBUG = 1# config('DEBUG', default=False, cast=bool)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('SECRET_KEY', default='string_from_.env')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

INTERNAL_IPS = []

INSTALLED_APPS = [
    'about.apps.AboutConfig',
    'posts.apps.PostsConfig',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'debug_toolbar',
    'sorl.thumbnail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'yatube.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'templates.context_processors.year',
            ],
        },
    },
]

WSGI_APPLICATION = 'yatube.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':
     'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':
     'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':
     'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':
     'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
#  STATIC_FILES = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = 'posts:index'
LOGOUT_REDIRECT_URL = 'https://www.youtube.com/watch?v=IA_evL-1F0wэ'
POSTS_ON_PAGE = 10

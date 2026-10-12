import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Configura DJANGO_SECRET_KEY o DJANGO_DEBUG=1 para desarrollo.')
    SECRET_KEY = 'development-only-do-not-use-in-production'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'remote']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
STATIC_URL = '/static/'
LANGUAGE_CODE = 'es'
TIME_ZONE = 'Europe/Madrid'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
ROBOT_DEMO = os.getenv('ROBOT_DEMO', '0') == '1'
ROBOT_DEVICE_ID = os.getenv('ROBOT_DEVICE_ID', '')
ROBOT_IP = os.getenv('ROBOT_IP', '')
ROBOT_LOCAL_KEY = os.getenv('ROBOT_LOCAL_KEY', '')
# Ordered enums confirmed for the owner's firmware; demo provides sample levels.
ROBOT_SUCTION_LEVELS = tuple(value.strip() for value in os.getenv('ROBOT_SUCTION_LEVELS', 'gentle,normal,strong' if ROBOT_DEMO else '').split(',') if value.strip())

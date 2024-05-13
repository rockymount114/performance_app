from pathlib import Path
import os
from decouple import config



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&1u1@wpg1y8rro8zmgi@%1fg%ju@fu$q^*%3tum&eds6a(!4zf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webapp',
    'crispy_forms',
    'easyaudit',

    'widget_tweaks', # for profile page
   
    
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
]

ROOT_URLCONF = 'crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
            'custom_tags':'webapp.template_tags.custom_tags'
            }
        },
    },
]

WSGI_APPLICATION = 'crm.wsgi.application'


# Database db_performance
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# 
# 
# 
# DROP database db_performance
# CREATE DATABASE db_performance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; 

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME" : "db_performance",
#         "USER" : "root",
#         "PASSWORD" : "",
#         "HOST" : "127.0.0.1",
#         "PORT" : "3306",  
#         'OPTIONS': {
#         'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#     }, 
#     }
# }

## SSQL Database connection

# SQL database

DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": "db_performance",
        "USER": "SSRS",
        "PASSWORD": "Ts4test@",
        "HOST": "172.20.21.115",
        "PORT": "1433",
        "OPTIONS": {"driver": "ODBC Driver 17 for SQL Server",
                    },
    },
}




AUTH_USER_MODEL = 'webapp.CustomerUser'

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_TZ = False # need to set as False if has setting for Time_ZONE


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# [BASE_DIR / 'static',]


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'

MEDIA_ROOT = 'media/'



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')







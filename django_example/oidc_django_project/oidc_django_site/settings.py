"""
Django settings

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from collections import OrderedDict
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'auth_app',
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',   #oidc module
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_app.apps.CustomConstance' # live settings
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auth_app.core.middleware.CustomOIDCSessionRefresh',
]

ROOT_URLCONF = 'oidc_django_site.urls'

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
        },
    },
]

WSGI_APPLICATION = 'oidc_django_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'auth_app.core.backends.CustomOIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    },
}

## Constance (OIDC) settings
# dict of OpenID Connect settings and their default values
OIDC_SETTINGS = {
    'OIDC_ENABLED': False,
    'OIDC_ISSUER_URL': "",
    'OIDC_RP_CLIENT_ID': "",
    'OIDC_RP_CLIENT_SECRET':"",
    'OIDC_RP_SCOPES':"",
    'OIDC_RP_SIGN_ALGO': "",
    'OIDC_CREATE_USER': True,
    'OIDC_OP_AUTHORIZATION_ENDPOINT':"",
    'OIDC_OP_TOKEN_ENDPOINT':"",
    'OIDC_OP_USER_ENDPOINT':"",
    'OIDC_OP_JWKS_ENDPOINT':"",
    'OIDC_OP_LOGOUT_ENDPOINT':"",
}

# SET THIS TO TRUE TO IMPORT SETTINGS FROM ENV. VARIABLES
# else, set defaults above or edit through Django Admin
OIDC_SETTINGS_FROM_ENV = True
#
# 
load_dotenv()
if OIDC_SETTINGS_FROM_ENV:
    print("loading default values from .env ...")
    for setting in OIDC_SETTINGS:
        if setting=="OIDC_CREATE_USER" or setting=="OIDC_ENABLED":
            OIDC_SETTINGS[setting] = True if os.getenv(setting) == "True" else False
        else:
            OIDC_SETTINGS[setting] = os.getenv(setting)

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# Custom configuration field
CONSTANCE_ADDITIONAL_FIELDS = {
    'sign_algo_select': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (("RS256", "RS256"), ("rs256", "RS256"), ("hs256", "HS256"))
    }],
}

# Dict of modifiable live settings 
CONSTANCE_CONFIG = OrderedDict([
    ('OIDC_ENABLED', (OIDC_SETTINGS['OIDC_ENABLED'], "Enable OpenID Connect")),
    ('OIDC_RP_CLIENT_ID', (OIDC_SETTINGS['OIDC_RP_CLIENT_ID'], "Client id")),
    ('OIDC_RP_CLIENT_SECRET', (OIDC_SETTINGS['OIDC_RP_CLIENT_SECRET'], "Client secret")),
    ('OIDC_ISSUER_URL', (OIDC_SETTINGS['OIDC_ISSUER_URL'], "Issuer URL")),
    ('OIDC_RP_SCOPES', (OIDC_SETTINGS['OIDC_RP_SCOPES'], "OIDC Scopes")),
    ('OIDC_CREATE_USER', (OIDC_SETTINGS['OIDC_CREATE_USER'], "Automatic Django user creation", bool)),
    ('OIDC_OP_AUTHORIZATION_ENDPOINT', (OIDC_SETTINGS['OIDC_OP_AUTHORIZATION_ENDPOINT'], "Authorization endpoint")),
    ('OIDC_OP_TOKEN_ENDPOINT', (OIDC_SETTINGS['OIDC_OP_TOKEN_ENDPOINT'], "Token endpoint")),
    ('OIDC_OP_USER_ENDPOINT', (OIDC_SETTINGS['OIDC_OP_USER_ENDPOINT'], "User endpoint")),
    ('OIDC_RP_SIGN_ALGO' , (OIDC_SETTINGS['OIDC_RP_SIGN_ALGO'], "Signature algorithm", "sign_algo_select")), 
    ('OIDC_OP_JWKS_ENDPOINT', (OIDC_SETTINGS['OIDC_OP_JWKS_ENDPOINT'], "JWKS endpoint")),
    ('OIDC_OP_LOGOUT_ENDPOINT', (OIDC_SETTINGS['OIDC_OP_LOGOUT_ENDPOINT'], "Logout endpoint")),
])

# live settings layout
CONSTANCE_CONFIG_FIELDSETS = {
    'General configuration': {
        'fields': ('OIDC_ENABLED','OIDC_ISSUER_URL', 'OIDC_RP_CLIENT_ID', 'OIDC_RP_CLIENT_SECRET', 'OIDC_RP_SCOPES', 'OIDC_CREATE_USER'),
    'collapse': False
    },
    'Advanced configuration': {
        'fields': ('OIDC_OP_AUTHORIZATION_ENDPOINT', 'OIDC_OP_TOKEN_ENDPOINT', 'OIDC_OP_USER_ENDPOINT', 'OIDC_OP_JWKS_ENDPOINT', 'OIDC_OP_LOGOUT_ENDPOINT', 'OIDC_RP_SIGN_ALGO'),
        'collapse': True
    },
}
# Custom auth classes for OIDC support 
OIDC_CALLBACK_CLASS = 'auth_app.views.CustomOIDCAuthenticationCallbackView'
OIDC_AUTHENTICATE_CLASS = 'auth_app.views.CustomOIDCAuthenticationRequestView'

OIDC_OP_LOGOUT_URL_METHOD = "auth_app.custom.provider_logout"

#Redirects
LOGIN_REDIRECT_URL = "http://localhost:8000/login_success"
LOGOUT_REDIRECT_URL = "http://localhost:8000/logout_success"
LOGIN_REDIRECT_URL_FAILURE = "http://localhost:8000/login_failure"

"""
Django settings for society_management project.
Production-ready: reads configuration from environment variables so the
same codebase runs locally (SQLite) and in production (Postgres + Cloudinary)
without code changes -- only environment variables differ.
"""

from pathlib import Path
import os
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core security settings (from environment) ---------------------------
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-^0_9k29jx(7e&4)z9w6qg^ror@w@-5d0@2-oufsl6)qyp5m12^'
)
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# Render provides its external hostname via this env var automatically.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Society Management apps
    'accounts',
    'core',
    'billing',
    'notices',
    'complaints',
    'visitors',
    'amenities',
    'staffmgmt',
]

# Cloudinary is optional: only enabled when CLOUDINARY_URL is set (production).
USE_CLOUDINARY = bool(config('CLOUDINARY_URL', default=''))
if USE_CLOUDINARY:
    INSTALLED_APPS = ['cloudinary_storage'] + INSTALLED_APPS + ['cloudinary']

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'society_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'society_management.wsgi.application'


# --- Database --------------------------------------------------------------
# Reads DATABASE_URL if present (Neon/Postgres in production); otherwise
# falls back to local SQLite so nothing changes for local development.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिंदी'),
    ('mr', 'मराठी'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']


# --- Static files (CSS/JS) served via WhiteNoise ---------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# --- Media files (uploads: photos, attachments) -----------------------------
# In production (Cloudinary configured) uploads persist permanently.
# Locally, they're just saved to the media/ folder on disk.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if USE_CLOUDINARY:
    STORAGES['default'] = {'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage'}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Security hardening (auto-enabled only when DEBUG=False) ---------------
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7  # 1 week, raise once confident
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True


# Email (console backend for dev; swap for a real SMTP backend in prod via env)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

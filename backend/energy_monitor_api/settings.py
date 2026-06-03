import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# СЕКРЕТНЫЕ ПАРАМЕТРЫ
# ============================================================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# ============================================================================
# ПОДКЛЮЧЕНИЕ К POSTGRESQL
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='energy_monitor_db'),
        'USER': config('DB_USER', default='energy_monitor'),
        'PASSWORD': config('DB_PASSWORD', default='admin437'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'application_name': 'energy_monitor_api',
        }
    }
}

# ============================================================================
# УСТАНОВЛЕННЫЕ ПРИЛОЖЕНИЯ
# ============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'devices.apps.DevicesConfig',
    'energy.apps.EnergyConfig',
]

# ============================================================================
# MIDDLEWARE
# ============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'energy_monitor_api.urls'

# ============================================================================
# TEMPLATES
# ============================================================================
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

WSGI_APPLICATION = 'energy_monitor_api.wsgi.application'

# ============================================================================
# ВАЛИДАЦИЯ ПАРОЛЕЙ
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# ИНТЕРНАЦИОНАЛИЗАЦИЯ
# ============================================================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Krasnoyarsk'
USE_I18N = True
USE_TZ = True

# ============================================================================
# СТАТИЧЕСКИЕ ФАЙЛЫ
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CORS КОНФИГУРАЦИЯ
# ============================================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# ============================================================================
# REST FRAMEWORK
# ============================================================================
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ============================================================================
# БЕЗОПАСНОСТЬ
# ============================================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'",),
        'style-src': ("'self'", "'unsafe-inline'"),
    }

AUTO_APPLY_MIGRATIONS = config('AUTO_APPLY_MIGRATIONS', default=True, cast=bool)


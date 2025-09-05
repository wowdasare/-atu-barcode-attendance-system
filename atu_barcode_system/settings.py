import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-123456789')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS configuration for Railway
ALLOWED_HOSTS = []
if 'RAILWAY_PUBLIC_DOMAIN' in os.environ:
    ALLOWED_HOSTS.append(os.environ.get('RAILWAY_PUBLIC_DOMAIN'))
if 'RAILWAY_STATIC_URL' in os.environ:
    railway_domain = os.environ.get('RAILWAY_STATIC_URL', '').replace('https://', '').replace('http://', '')
    if railway_domain:
        ALLOWED_HOSTS.append(railway_domain)

# Add custom hosts from environment
custom_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS.extend(custom_hosts.split(','))

# Remove duplicates and empty strings
ALLOWED_HOSTS = list(filter(None, set(ALLOWED_HOSTS)))

# For development
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0'])

# Railway domains (fallback)
ALLOWED_HOSTS.extend(['.railway.app', '.up.railway.app'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'attendance',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'atu_barcode_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'atu_barcode_system.wsgi.application'

# Database configuration
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() == 'true'

# Add Railway domain to CORS when deployed
if 'RAILWAY_STATIC_URL' in os.environ:
    railway_domain = os.environ.get('RAILWAY_STATIC_URL', '').replace('https://', '')
    if railway_domain:
        CORS_ALLOWED_ORIGINS.append(f"https://{railway_domain}")

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF settings for API - must include scheme (https://) for Django 4.0+
CSRF_TRUSTED_ORIGINS = []

# Check common Railway environment variables and ensure they have https:// scheme
potential_railway_vars = [
    'RAILWAY_STATIC_URL',
    'RAILWAY_PUBLIC_DOMAIN', 
    'RAILWAY_DOMAIN',
    'PUBLIC_DOMAIN',
    'DOMAIN'
]

for var_name in potential_railway_vars:
    if var_name in os.environ:
        raw_domain = os.environ.get(var_name, '')
        if raw_domain and raw_domain.strip():
            # Ensure it has https:// scheme
            if not raw_domain.startswith(('http://', 'https://')):
                domain_with_scheme = f'https://{raw_domain.strip()}'
            else:
                domain_with_scheme = raw_domain.strip()
            
            if domain_with_scheme not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(domain_with_scheme)

# Add Railway domain patterns as fallbacks
CSRF_TRUSTED_ORIGINS.extend([
    'https://*.railway.app',
    'https://*.up.railway.app',
])

# Final cleanup: ensure all origins have proper scheme and remove duplicates
final_origins = []
for origin in CSRF_TRUSTED_ORIGINS:
    if origin and not origin.startswith(('http://', 'https://')):
        origin = f'https://{origin}'
    if origin and origin not in final_origins:
        final_origins.append(origin)

CSRF_TRUSTED_ORIGINS = final_origins
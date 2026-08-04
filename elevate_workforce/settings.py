import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-elevate-local-dev-key-123456789"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"

# Hostnames allowed to access the site (Note: Port numbers must not be included here)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]
# Render provides its external hostname via this environment variable at runtime
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Additional production hosts (comma-separated) supplied via environment variable,
# e.g. ALLOWED_HOSTS_EXTRA=example.com,www.example.com
ALLOWED_HOSTS_EXTRA = os.environ.get("ALLOWED_HOSTS_EXTRA", "")
if ALLOWED_HOSTS_EXTRA:
    ALLOWED_HOSTS += [host.strip() for host in ALLOWED_HOSTS_EXTRA.split(",") if host.strip()]

# CSRF Trusted Origins to allow secure POST requests across local development ports
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://127.0.0.1:9000',
    'http://localhost:9000',
]

# Production HTTPS origins, supplied via environment variable
# e.g. CSRF_TRUSTED_ORIGINS_EXTRA=https://example.com,https://www.example.com
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

CSRF_TRUSTED_ORIGINS_EXTRA = os.environ.get("CSRF_TRUSTED_ORIGINS_EXTRA", "")
if CSRF_TRUSTED_ORIGINS_EXTRA:
    CSRF_TRUSTED_ORIGINS += [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_EXTRA.split(",") if origin.strip()]

# Application definition

INSTALLED_APPS = [
    # Core Admin Panel styling and WhiteNoise development handler
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # WhiteNoise handler for development server
    'django.contrib.staticfiles',
    
    # Third-Party Integrations
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Custom Apps
    'core',
    'jobs',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Compression & caching for static assets
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'elevate_workforce.urls'

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
                'core.context_processors.seo_settings',  # Connects dynamic global SEO variables
            ],
        },
    },
]

WSGI_APPLICATION = 'elevate_workforce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Custom User Model configuration
# Tells Django to use the CustomUser model defined in users/models.py
AUTH_USER_MODEL = 'users.CustomUser'


# Authentication Backend Routing Configurations
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:dashboard'
LOGOUT_REDIRECT_URL = 'core:index'


# Crispy Forms styling integration configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage engine for static file compression and caching
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# Media files (Resumes, company logos, and other uploads)
# https://docs.djangoproject.com/en/6.0/topics/files/

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# SECURITY SETTINGS (AUTOMATIC LOCAL DEV VS PRODUCTION)
# ==============================================================================

if DEBUG:
    # Local Development Settings (Enables plain HTTP, disables secure redirects)
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    # Production Settings (Forces secure HTTPS connections)
    # WARNING: Only keep these True if your production server has an SSL certificate configured.
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Additional security headers (applied in both local and production environments)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Set DEBUG based on environment variable - default to False for security
DEBUG = os.getenv("DEBUG", "False") == "True"

# Secret key configuration - CRITICAL for security
# In production, this MUST be set as an environment variable
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    if DEBUG:
        # Only use this in development, never in production
        SECRET_KEY = "insecure-dev-key-for-local-development-only"
        print("WARNING: Using insecure development SECRET_KEY. Never use this in production!")
    else:
        raise Exception(
            "Production environment detected but no SECRET_KEY provided. "
            "This is a security risk. Please set the SECRET_KEY environment variable."
        )

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# CSRF trusted origins for production
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "https://127.0.0.1,https://localhost").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',

    # Apps del proyecto
    'website',
    'services',
    'demos',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'miweb.middleware.SecurityProtectionMiddleware',  # Middleware personalizado para protección
]

# Optimizar middleware en producción
if not DEBUG:
    # Añadir middleware de gzip para compresión de respuestas HTTP
    MIDDLEWARE.insert(1, 'django.middleware.gzip.GZipMiddleware')
    
    # Añadir middleware de etag condicional
    MIDDLEWARE.append('django.middleware.http.ConditionalGetMiddleware')

ROOT_URLCONF = 'miweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # plantillas globales
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

WSGI_APPLICATION = 'miweb.wsgi.application'

# DB: usa SQLite en dev (más tarde cambiamos a Postgres)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]



# ---- Gemini ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ---- Destinatarios correo ----
DEFAULT_TO_EMAIL = os.getenv("DEFAULT_TO_EMAIL", "you@example.com")
CONTACT_RECIPIENTS = [
    e.strip() for e in os.getenv("CONTACT_RECIPIENTS", DEFAULT_TO_EMAIL).split(",") if e.strip()
]

# ---- Email/SMTP ----
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@localhost")
LEAD_TO_EMAIL      = os.getenv("LEAD_TO_EMAIL", "")

EMAIL_BACKEND   = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST      = os.getenv("EMAIL_HOST", "")
EMAIL_PORT      = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS   = os.getenv("EMAIL_USE_TLS", "False") == "True"
EMAIL_USE_SSL   = os.getenv("EMAIL_USE_SSL", "False") == "True"
LANGUAGE_CODE = 'es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configurar el cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutos
    }
}

# Activar cache de templates en producción
if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False  # Deshabilitar APP_DIRS cuando usamos loaders
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Content security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    
    # Prevent clickjacking (already using the middleware)
    X_FRAME_OPTIONS = 'DENY'

# URLs que están exentas de la protección de Content Security Policy
# Útil para páginas que necesitan cargar recursos externos
CSP_EXEMPT_URLS = [
    '/admin/',
    '/demos/',
]

# Configuración de logging simplificada para producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Mantener autenticación de sesión
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ) if not DEBUG else (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

# JWT settings - solo se usa si ENABLE_JWT_AUTH = True
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Configuración de características de seguridad avanzadas
# Todas estas características son OPCIONALES y están DESACTIVADAS por defecto
# Para activarlas en producción, añade estas variables a tu .env

# Habilitar el proxy de API (por defecto: False)
ENABLE_API_PROXY = os.getenv('ENABLE_API_PROXY', 'False') == 'True'

# Habilitar la autenticación JWT (por defecto: False)
ENABLE_JWT_AUTH = os.getenv('ENABLE_JWT_AUTH', 'False') == 'True'

# Añadir el middleware de proxy de API solo si está habilitado
if ENABLE_API_PROXY:
    MIDDLEWARE.append('miweb.security.api_proxy.APIProxyMiddleware')

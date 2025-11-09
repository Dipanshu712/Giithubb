from pathlib import Path
import os
from django.contrib.messages import constants as message_constants
# from dotenv import load_dotenv
import dj_database_url

# Load environment variables
# load_dotenv()


# Remove load_dotenv() on Railway
if os.getenv("RAILWAY_ENVIRONMENT") != "production":
    from dotenv import load_dotenv
    load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# SECURITY
# ==========================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key')

# RAILWAY sets RAILWAY_ENVIRONMENT = "production" in deployed app
DEBUG = os.getenv("RAILWAY_ENVIRONMENT") != "production"

ALLOWED_HOSTS = ["*"]

# ==========================
# INSTALLED APPS
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # custom apps
    'ecommerceapp',
    'authcart',
    'django.contrib.humanize',
]

# ==========================
# MIDDLEWARE
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==========================
# URL & TEMPLATES
# ==========================
ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# ==========================
# DATABASE (Railway + Local)
# ==========================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Always use your .env DATABASE_URL first — avoids Railway internal host issue
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Local fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==========================
# STATIC & MEDIA FILES
# ==========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================
# EMAIL SETTINGS (Gmail SMTP)
# ==========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'mdipanshu713@gmail.com'  # your fixed email
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # app password

# ==========================
# MESSAGE TAGS
# ==========================
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger',
    message_constants.WARNING: 'warning',
    message_constants.SUCCESS: 'success',
    message_constants.INFO: 'info',
}

# ==========================
# RAZORPAY
# ==========================
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

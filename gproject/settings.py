"""
Django settings for gproject project.
"""

import os
from pathlib import Path
from django.contrib import messages
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ================= SECURITY =================
SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Railway domain from environment
RAILWAY_HOST = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")

# Allow ALL hosts (Railway uses dynamic hostnames)
ALLOWED_HOSTS = ["*"]

# ================= CSRF FIX FOR RAILWAY =================
CSRF_TRUSTED_ORIGINS = []

# Add Railway HTTPS host
if RAILWAY_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_HOST}")

# These two must be enabled for Railway reverse proxy HTTPS
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------- APPS ----------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'gprojectapp',
    'authcart',

    'widget_tweaks',
    'cloudinary',
    'cloudinary_storage',
]

# ---------------- MIDDLEWARE ----------------
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

ROOT_URLCONF = 'gproject.urls'
WSGI_APPLICATION = 'gproject.wsgi.application'

# ---------------- TEMPLATES ----------------
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
                'gprojectapp.context_processors.categories_processor',
                'gprojectapp.context_processors.mega_menu',
            ],
        },
    },
]

# ---------------- DATABASE ----------------
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',  # fallback for local
        conn_max_age=600,
        ssl_require=True
    )
}

# ---------------- EMAIL ----------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

# ---------------- STATIC ----------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------- MEDIA ----------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------- CLOUDINARY ----------------
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# ---------------- AUTH ----------------
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"

# ---------------- MESSAGES ----------------
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
}

# ---------------- OTHER ----------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week


"""
Django settings for blinkit project.
"""

from pathlib import Path
import os
import sys
import dj_database_url


# ==========================================
# BASE DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# SECURITY SETTINGS
# ==========================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-change-this-for-production"
)

# Enable DEBUG locally when running the Django development server.
# On Render, DEBUG should be set to False.
DEBUG = (
    os.environ.get("DEBUG", "False").lower() == "true"
    or ("runserver" in sys.argv and "RENDER" not in os.environ)
)

ALLOWED_HOSTS = [
    "buyzo-f3gm.onrender.com",
    "localhost",
    "127.0.0.1",
]

# Allow additional hosts through an environment variable if required.
extra_hosts = os.environ.get("ALLOWED_HOSTS", "")
if extra_hosts:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in extra_hosts.split(",")
        if host.strip()
    )


# ==========================================
# APPLICATIONS
# ==========================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================================
# URL CONFIGURATION
# ==========================================

ROOT_URLCONF = "blinkit.urls"


# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==========================================
# WSGI CONFIGURATION
# ==========================================

WSGI_APPLICATION = "blinkit.wsgi.application"


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ==========================================
# STATIC FILES (CSS, JAVASCRIPT)
# ==========================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# ==========================================
# MEDIA FILES (BANNERS AND PRODUCT IMAGES)
# ==========================================

MEDIA_URL = "/media/"

MEDIA_ROOT = Path(
    os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media"))
)

# Optional: enable Django to serve media through a view.
# This is useful for a small deployment or temporary testing.
# Set SERVE_MEDIA_WITH_DJANGO=True on Render to enable it.
SERVE_MEDIA_WITH_DJANGO = (
    os.environ.get("SERVE_MEDIA_WITH_DJANGO", "False").lower()
    == "true"
)


# ==========================================
# DEFAULT PRIMARY KEY
# ==========================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================================
# SESSION SETTINGS
# ==========================================

SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_COOKIE_NAME = "buyzo_session"

SESSION_COOKIE_AGE = 86400

SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"


# ==========================================
# CSRF AND HTTPS SETTINGS
# ==========================================

CSRF_TRUSTED_ORIGINS = [
    "https://buyzo-f3gm.onrender.com",
]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

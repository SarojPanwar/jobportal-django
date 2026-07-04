"""
Django settings for the JobConnect project (jobportal).

Converted from the original Flask + SQLite app.
Database: MySQL (via env vars) — falls back to SQLite only if
explicitly requested for quick local testing.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ─── Core security settings ──────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    h.strip() 
    for h in os.environ.get(
        "ALLOWED_HOSTS", 
        "127.0.0.1,localhost,evarasingh.pythonanywhere.com"
        ).split(",") if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
     "https://evarasingh.pythonanywhere.com",
]



# ─── Applications ─────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

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

ROOT_URLCONF = "jobportal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "jobportal.wsgi.application"


# ─── Database ─────────────────────────────────────────────────────────────
# Set DATABASE_URL, e.g.:
#   mysql://USER:PASSWORD@HOST:3306/DBNAME
# in your .env file (or Vercel project env vars).
# Falls back to individual MYSQL_* vars, and finally to local SQLite
# only when nothing is configured (handy for a first `runserver` test).

DATABASE_URL = os.environ.get("DATABASE_URL")
DB_SSL_REQUIRE = os.environ.get("DB_SSL_REQUIRE", "True") == "True"

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
    # dj_database_url's ssl_require flag adds a "sslmode" option, which is
    # PostgreSQL-only syntax and breaks PyMySQL/mysqlclient. For MySQL we
    # need to set OPTIONS the way PyMySQL actually expects instead.
    if DATABASES["default"].get("ENGINE") == "django.db.backends.mysql":
        DATABASES["default"].setdefault("OPTIONS", {})["charset"] = "utf8mb4"
        if DB_SSL_REQUIRE:
            DATABASES["default"]["OPTIONS"]["ssl"] = {"ssl_mode": "REQUIRED"}
elif os.environ.get("MYSQL_DATABASE"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DATABASE"),
            "USER": os.environ.get("MYSQL_USER", "root"),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
            "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ─── Custom user model & auth ──────────────────────────────────────────────
AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = [
    "core.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "core:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:index"

# Map Flask's 'danger' category to Django's default 'error' tag so the
# existing Bootstrap alert classes (alert-danger / alert-success / ...) work.
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─── Internationalization ──────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ─── Static files ───────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Default admin credentials, used by `python manage.py seed_admin`
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@jobportal.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

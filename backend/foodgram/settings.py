import os as system_os
from pathlib import Path as PathLibPath
from django.core.management.utils import get_random_secret_key as generate_secret
from dotenv import load_dotenv as load_envars

ROOT_PATH = PathLibPath(__file__).resolve().parent.parent

load_envars(system_os.path.join(ROOT_PATH, "..", "infra", ".env"))

CONFIG = {
    "SECURITY": {
        "KEY": system_os.getenv("DJANGO_SECRET_KEY", generate_secret()),
        "DEBUG": system_os.getenv("DJANGO_DEBUG", "false").lower() == "true",
        "HOSTS": system_os.getenv("ALLOWED_HOSTS", "").split(","),
        "CORS": system_os.getenv("CORS_ALLOWED_HOSTS", "").split(",")
    },
    "APPS": [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "rest_framework",
        "rest_framework.authtoken",
        "corsheaders",
        "djoser",
        "django_filters",
        "ingredients.apps.IngredientConfig",
        "users.apps.UsersConfig",
        "recipes.apps.RecipesConfig",
    ],
    "MIDDLEWARE": [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    "DATABASE": {
        "default": {
            "ENGINE": "django.db.backends." + system_os.getenv("DB_ENGINE", "sqlite3"),
            "NAME": system_os.getenv("DB_NAME", ROOT_PATH / "db.sqlite3"),
            "USER": system_os.getenv("DB_USER", "django"),
            "PASSWORD": system_os.getenv("DB_PASSWORD", ""),
            "HOST": system_os.getenv("DB_HOST", "localhost"),
            "PORT": system_os.getenv("DB_PORT", 5432),
        }
    },
    "TEMPLATES": [{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }],
    "AUTH": {
        "VALIDATORS": [
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ],
        "USER_MODEL": "users.BlogerUser"
    },
    "LOCALIZATION": {
        "LANGUAGE": "ru-RU",
        "TIMEZONE": "Europe/Moscow",
        "USE_I18N": True,
        "USE_TZ": True
    },
    "STATIC": {
        "URL": "/static_backend/",
        "ROOT": system_os.path.join(ROOT_PATH, "static_backend")
    },
    "MEDIA": {
        "URL": "/media_backend/",
        "ROOT": ROOT_PATH / "media_backend"
    },
    "DJOSER_CONFIG": {
        "LOGIN_FIELD": "email",
        "HIDE_USERS": False,
        "USER_CREATE_PASSWORD_RETYPE": False,
        "SERIALIZERS": {
            "user": "api.serializers.EnhancedUserSerializer",
            "current_user": "api.serializers.EnhancedUserSerializer",
        },
        "PERMISSIONS": {
            "activation": ["rest_framework.permissions.AllowAny"],
            "password_reset_confirm": ["rest_framework.permissions.AllowAny"],
            "username_reset_confirm": ["rest_framework.permissions.AllowAny"],
            "set_username": ["djoser.permissions.CurrentUserOrAdmin"],
            "user_create": ["rest_framework.permissions.AllowAny"],
            "set_password": ["djoser.permissions.CurrentUserOrAdmin"],
            "username_reset": ["rest_framework.permissions.AllowAny"],
            "token_create": ["rest_framework.permissions.AllowAny"],
            "token_destroy": ["rest_framework.permissions.IsAuthenticated"],
            "user_delete": ["djoser.permissions.CurrentUserOrAdmin"],
            "user": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
            "user_list": ["rest_framework.permissions.AllowAny"],
        }
    },
    "FILE_UPLOADS": {
        "AVATAR": "users/images/",
        "RECIPES": "recipes/images/"
    },
    "URL_SHORTENER": {
        "CHARS": "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz1234567890",
        "TOKEN_LEN": 6
    },
    "SHOPPING_LIST": {
        "FILE_NAME": "shopping_list"
    }
}

REST_API_SETTINGS = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "PAGINATION": {
        "CLASS": "core.pagination.CustomPagePaginator",
        "ITEMS_PER_PAGE": 6,
    },
}

SECRET_KEY = CONFIG["SECURITY"]["KEY"]
DEBUG = CONFIG["SECURITY"]["DEBUG"]
ALLOWED_HOSTS = CONFIG["SECURITY"]["HOSTS"]
CORS_ALLOWED_ORIGINS = CONFIG["SECURITY"]["CORS"]
INSTALLED_APPS = CONFIG["APPS"]
MIDDLEWARE = CONFIG["MIDDLEWARE"]
ROOT_URLCONF = "foodgram.urls"
TEMPLATES = CONFIG["TEMPLATES"]
WSGI_APPLICATION = "foodgram.wsgi.application"
DATABASES = CONFIG["DATABASE"]
AUTH_PASSWORD_VALIDATORS = CONFIG["AUTH"]["VALIDATORS"]
LANGUAGE_CODE = CONFIG["LOCALIZATION"]["LANGUAGE"]
TIME_ZONE = CONFIG["LOCALIZATION"]["TIMEZONE"]
USE_I18N = CONFIG["LOCALIZATION"]["USE_I18N"]
USE_TZ = CONFIG["LOCALIZATION"]["USE_TZ"]
STATIC_URL = CONFIG["STATIC"]["URL"]
STATIC_ROOT = CONFIG["STATIC"]["ROOT"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MEDIA_URL = CONFIG["MEDIA"]["URL"]
MEDIA_ROOT = CONFIG["MEDIA"]["ROOT"]
REST_FRAMEWORK = {
    key: value for key, value in [
        ("DEFAULT_PERMISSION_CLASSES", REST_API_SETTINGS["DEFAULT_PERMISSION_CLASSES"]),
        ("DEFAULT_AUTHENTICATION_CLASSES", REST_API_SETTINGS["DEFAULT_AUTHENTICATION_CLASSES"]),
        ("DEFAULT_PAGINATION_CLASS", REST_API_SETTINGS["PAGINATION"]["CLASS"]),
        ("PAGE_SIZE", REST_API_SETTINGS["PAGINATION"]["ITEMS_PER_PAGE"]),
    ]
}
AUTH_USER_MODEL = CONFIG["AUTH"]["USER_MODEL"]
DJOSER = CONFIG["DJOSER_CONFIG"]
UPLOAD_AVATAR = CONFIG["FILE_UPLOADS"]["AVATAR"]
UPLOAD_RECIPES = CONFIG["FILE_UPLOADS"]["RECIPES"]
CHARACTERS_SHORT_URL = CONFIG["URL_SHORTENER"]["CHARS"]
TOKEN_LENGTH_SHORT_URL = CONFIG["URL_SHORTENER"]["TOKEN_LEN"]
NAME_SHOPPING_CART_LIST_FILE = CONFIG["SHOPPING_LIST"]["FILE_NAME"]
"""
워크드 안전거래 플랫폼 - Django Settings
"""
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # Local apps
    'accounts.apps.AccountsConfig',
    'properties.apps.PropertiesConfig',
    'contracts.apps.ContractsConfig',
    'insurance.apps.InsuranceConfig',
    'reviews.apps.ReviewsConfig',
    'schedules.apps.SchedulesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'workd_project.urls'

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

WSGI_APPLICATION = 'workd_project.wsgi.application'

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', f"postgres://{os.environ.get('DB_USER', 'workd_user')}:{os.environ.get('DB_PASSWORD', 'workd_pass')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'workd_db')}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_USER_MODEL = 'accounts.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,https://contract-platform-final.vercel.app'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins for login
CSRF_TRUSTED_ORIGINS = [
    'https://contract-backend-final.onrender.com',
    'https://*.vercel.app'
]

# Static / Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise storage for compressed static files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Celery (비동기 알림 처리)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 알림톡 설정
KAKAO_API_KEY = os.environ.get('KAKAO_API_KEY', '')
KAKAO_SENDER_KEY = os.environ.get('KAKAO_SENDER_KEY', '')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# NHN Cloud 알림 설정 (검수 완료 후 Mock 모드 해제)
NHN_MOCK_MODE = os.environ.get('NHN_MOCK_MODE', 'False') == 'True'
NHN_ALIMTALK_UNDER_REVIEW = os.environ.get('NHN_ALIMTALK_UNDER_REVIEW', 'True') == 'True'

# NHN Cloud SMS
NHN_SMS_APPKEY = os.environ.get('NHN_SMS_APPKEY', '')
NHN_SMS_SECRET = os.environ.get('NHN_SMS_SECRET', '')
NHN_SMS_SENDER = os.environ.get('NHN_SMS_SENDER', '')

# NHN Cloud Alimtalk
NHN_ALIMTALK_APPKEY = os.environ.get('NHN_ALIMTALK_APPKEY', '')
NHN_ALIMTALK_SECRET = os.environ.get('NHN_ALIMTALK_SECRET', '')
NHN_ALIMTALK_SENDERKEY = os.environ.get('NHN_ALIMTALK_SENDERKEY', '')

# NHN Cloud Email
NHN_EMAIL_APPKEY = os.environ.get('NHN_EMAIL_APPKEY', '')
NHN_EMAIL_SECRET = os.environ.get('NHN_EMAIL_SECRET', '')
NHN_EMAIL_SENDER = os.environ.get('NHN_EMAIL_SENDER', '')

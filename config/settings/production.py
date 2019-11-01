from .base import *
import os

ALLOWED_HOSTS = ['0.0.0.0', '192.168.99.21', 'localhost', '127.0.0.1']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', True)

SECRET_KEY = env('DJANGO_SECRET_KEY', default='#u23r6)y(wh_^i4$gi&ic4^r@4m&f&83)xcuo$dtz%=lq8iu*u')


print("production file ------------")

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_BACKEND_URL = "redis://redis:6379/0"

BROKER_URL = "redis://redis:6379/0"
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600} 
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_IMPORTS = ("project.api.tasks", )

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    },
    'original': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(ROOT_DIR.path('db.sqlite3')),
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
    'with-sentinel': {
        'SENTINELS': [('redis', 26736), ('redis', 26737)],
        'MASTER_NAME': 'redismaster',
        'DB': 0,
        'PASSWORD': 'secret',
        'SOCKET_TIMEOUT': None,
        'CONNECTION_KWARGS': {
            'socket_connect_timeout': 0.3
        },
    },
    'high': {
        'URL': os.getenv('REDISTOGO_URL', 'redis://redis:6379/0'), # If you're on Heroku
        'DEFAULT_TIMEOUT': 500,
    },
    'low': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
    }
}



"""Contains config variables for keepno app."""

import os
from pathlib import Path


# Secret key
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')


# Root project directory
BASEDIR = Path(__file__).parent.parent.resolve()


# Debug
FLASK_DEBUG = os.environ.get('FLASK_DEBUG')


# Database
SQLALCHEMY_DATABASE_USER = os.environ.get('SQLALCHEMY_DATABASE_USER')
SQLALCHEMY_DATABASE_PASSWORD = os.environ.get('SQLALCHEMY_DATABASE_PASSWORD')
SQLALCHEMY_DATABASE_HOST = os.environ.get('SQLALCHEMY_DATABASE_HOST')
SQLALCHEMY_DATABASE_PORT = os.environ.get('SQLALCHEMY_DATABASE_PORT')
SQLALCHEMY_DATABASE_DB = os.environ.get('SQLALCHEMY_DATABASE_DB')

SQLALCHEMY_DATABASE_URI = f'postgresql://{SQLALCHEMY_DATABASE_USER}:{SQLALCHEMY_DATABASE_PASSWORD}' \
                          f'@{SQLALCHEMY_DATABASE_HOST}:{SQLALCHEMY_DATABASE_PORT}/{SQLALCHEMY_DATABASE_DB}'


# Medias
MEDIA_ROOT = Path(BASEDIR) / 'app' / 'media'
MEDIA_NOTES_PDF = Path(BASEDIR) / 'app' / 'media' / 'notes' / 'pdf'


# Note pagination
NOTES_PER_PAGE = 5
ENTRIES_PER_PAGE = 2


# Redis
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'


# Celery
CELERY_CONFIG = {
    'broker_url': REDIS_URL,
    'result_backend': REDIS_URL,
    'include': [
        'app.notes.tasks'
    ]
}

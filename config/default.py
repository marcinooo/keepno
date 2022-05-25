"""Contains config variables for keepno app."""

import os
import socket
from pathlib import Path


# Secret key
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')


# Root project directory
BASEDIR = Path(__file__).parent.parent.resolve()


# Debug
FLASK_DEBUG = True


# Testing
TESTING = False


# Server name
SERVER_NAME = '192.168.1.43:5000'


# Database
DATABASE_URI = os.environ.get('DATABASE_URI')

if DATABASE_URI is not None:
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
else:
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
        'app.notes.tasks',
        'app.accounts.tasks'
    ]
}


# Recaptcha
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PARAMETERS = {'hl': 'en'}


# Mail
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT'))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS').lower() in ('true', '1', 't')
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL').lower() in ('true', '1', 't')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_OFFICIAL_SITE_ADDRESS = os.environ.get('MAIL_OFFICIAL_SITE_ADDRESS')

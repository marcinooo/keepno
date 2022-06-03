"""Contains two main functions to create keepno app."""

import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from celery import Celery

from .mail import SES


db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
login_manager = LoginManager()
ses = SES()


def create_app() -> Flask:
    """Main app function."""
    flask_env = os.environ.get('FLASK_ENV')
    if flask_env == 'development':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.development'
    elif flask_env == 'production':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.production'
    elif flask_env == 'testing':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.testing'
    else:
        raise NotImplementedError('Please set "FLASK_ENV" variable to "development" or "production", or "testing".')

    load_dotenv(env_file)

    config = Path(__file__).parent.absolute() / '..' / 'config' / 'default.py'
    template_folder = Path(__file__).parent.absolute() / 'templates'
    static_folder = Path(__file__).parent.absolute() / 'static'

    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder, instance_relative_config=True)
    app.config.from_pyfile(config)

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'accounts.login'
    ses.init_app(app)

    from .notes import notes_blueprint  # pylint: disable=import-outside-toplevel
    from .accounts import accounts_blueprint  # pylint: disable=import-outside-toplevel
    from .views import register_error_handlers  # pylint: disable=import-outside-toplevel
    app.register_blueprint(notes_blueprint)
    app.register_blueprint(accounts_blueprint)
    register_error_handlers(app)

    return app


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name)
    celery.conf.update(app.config.get('CELERY_CONFIG', {}))
    TaskBase = celery.Task

    class ContextTask(TaskBase):  # pylint: disable=too-few-public-methods
        """Creates task with current app context."""
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


# pylint: disable=wrong-import-position,unused-import
from .notes import models as notes_models
from .accounts import models as accounts_models

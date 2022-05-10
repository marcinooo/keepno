import os
from flask import Flask, render_template
from pathlib import Path
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


db = SQLAlchemy()
ma = Marshmallow()


def create_app() -> Flask:
    flask_env = os.environ.get('FLASK_ENV')
    if flask_env == 'development':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.development'
    elif flask_env == 'production':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.production'
    elif flask_env == 'testing':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.testing'
    else:
        raise NotImplemented('Please set "FLASK_ENV" variable to "development" or "production", or "testing".')

    load_dotenv(env_file)

    config = Path(__file__).parent.absolute() / '..' / 'config' / 'default.py'
    template_folder = Path(__file__).parent.absolute() / 'templates'
    static_folder = Path(__file__).parent.absolute() / 'static'

    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder, instance_relative_config=True)
    app.config.from_pyfile(config)

    db.init_app(app)
    ma.init_app(app)

    from .notes import notes_blueprint
    app.register_blueprint(notes_blueprint)

    return app

from .notes import models as notes_models

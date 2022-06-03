"""
The script contains fixture which prepares flask client for tests.
"""

import os
import sys
import pytest

from .resources import NOTE, ENTRY

test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(test_dir, '..', '..'))

from app import create_app, db, notes_models, accounts_models


@pytest.fixture
def client():
    os.environ["FLASK_ENV"] = 'testing'
    app = create_app()
    with app.test_client() as client:
        with app.app_context() as ctx:
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def note(client):
    note = notes_models.Note(**NOTE)
    note.save_to_db()
    yield
    note.delete_from_db()


@pytest.fixture
def entry(note):
    notes = notes_models.Note.get_all()
    note_id = notes[0].id
    entry = notes_models.Entry(note_id=note_id, **ENTRY)
    entry.save_to_db()
    yield entry
    entry.delete_from_db()


@pytest.fixture
def user():
    password_hash = accounts_models.User.generate_password_hash('Jofken35')
    new_user = accounts_models.User(username='John',
                                    email='john.kennedy@gmail.com',
                                    password=password_hash)
    new_user_profile = accounts_models.Profile(user=new_user)
    new_user.save_to_db()
    new_user_profile.save_to_db()
    yield new_user
    new_user_profile.delete_from_db()
    new_user.delete_from_db()


def request_loader(client, user):
    """
    The function load user. It allows make authenticated client in tests.
    :param client: test client
    :param user: User to load
    :return: None
    """
    @client.application.login_manager.request_loader
    def load_user_from_request(_):
        return user


@pytest.fixture
def auth_client(client, user):
    user.active = True
    user.save_to_db()

    request_loader(client, user)
    yield client
    request_loader(client, None)

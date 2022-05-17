"""
The script contains fixture which prepares flask client for tests.
"""

import os
import sys
import pytest

from .resources import NOTE, ENTRY

test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(test_dir, '..', '..'))

from app import create_app, db, notes_models


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

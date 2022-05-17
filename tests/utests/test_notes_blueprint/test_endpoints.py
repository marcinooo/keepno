"""
Contains unit tests of endpoints.
"""
from tests.utests.resources import NOTE, ENTRY

from app import notes_models


def test_note_template_getting(client, note, entry):
    response = client.get('/notes/1')
    html_page = response.data.decode('utf-8')

    assert html_page.startswith('<!doctype html>')
    assert NOTE['title'] in html_page
    assert NOTE['description'] in html_page
    assert ENTRY['content'] not in html_page
    assert html_page.endswith('</html>')


def test_note_export_template_getting(client, note, entry):
    response = client.get('/notes/1/export')
    html_page = response.data.decode('utf-8')

    assert html_page.startswith('<!doctype html>')
    assert NOTE['title'] in html_page
    assert NOTE['description'] in html_page
    assert 'Generate PDF' in html_page
    assert html_page.endswith('</html>')


def test_api_notes_getting(client, note, entry):
    response = client.get('/api/notes')
    data = response.json

    assert data['notes'][0]['title'] == NOTE['title']
    assert data['has_next'] is False
    assert data['next_num'] is None


def test_api_notes_adding(client):
    note_title = 'Note title'
    note_description = 'Note description'
    response = client.post('/api/notes', json={
        'title': note_title,
        'description': note_description
    })
    data = response.json

    assert data['note']['title'] == note_title
    assert data['note']['description'] == note_description
    notes = notes_models.Note.get_all()
    assert notes[0].title == note_title
    assert notes[0].description == note_description


def test_api_notes_adding_with_invalid_title(client):
    note_title = ''
    note_description = 'Note description'
    response = client.post('/api/notes', json={
        'title': note_title,
        'description': note_description
    })
    data = response.json

    notes = notes_models.Note.get_all()
    assert response.status_code == 400
    assert notes == []


def test_api_entries_getting(client, note, entry):
    response = client.get('/api/notes/1/entries')
    data = response.json

    assert data['entries'][0]['content'] == ENTRY['content']
    assert data['has_next'] is False
    assert data['next_num'] is None


def test_api_entries_adding(client, note):
    notes = notes_models.Note.get_all()
    note_id = notes[0].id
    entry_content = 'Entry content'
    response = client.post('/api/notes/1/entries', json={
        'content': entry_content,
        'note_id': note_id
    })
    data = response.json

    assert data['entry']['content'] == entry_content
    assert data['entry']['note_id'] == note_id
    entries = notes_models.Entry.get_all()
    assert entries[0].content == entry_content
    assert entries[0].note_id == note_id


def test_api_entries_adding_with_invalid_content(client, note):
    notes = notes_models.Note.get_all()
    note_id = notes[0].id
    entry_content = ''
    response = client.post('/api/notes/1/entries', json={
        'content': entry_content,
        'note_id': note_id
    })
    data = response.json

    entries = notes_models.Entry.get_all()
    assert response.status_code == 400
    assert entries == []


def test_api_entries_updating(client, note, entry):
    new_entry_content = 'New super content'
    notes = notes_models.Note.get_all()
    note_id = notes[0].id
    response = client.put('/api/notes/1/entries/1', json={
        'content': new_entry_content,
    })
    data = response.json

    assert data['entry']['content'] == new_entry_content
    entries = notes_models.Entry.get_all()
    assert entries[0].content == new_entry_content


def test_api_entries_updating_with_invalid_content(client, note, entry):
    notes = notes_models.Note.get_all()
    note_id = notes[0].id
    entries = notes_models.Entry.get_all()
    entry_id =  entries[0].id
    entry_content = entries[0].content
    response = client.put(f'/api/notes/1/entries/{entry_id}', json={
        'content': '',
    })
    data = response.json

    entries = notes_models.Entry.get_all()
    assert entries[0].content == entry_content


def test_api_entries_deleting(client, note, entry):
    response = client.delete('/api/notes/1/entries/1')
    data = response.json

    entries = notes_models.Entry.get_all()
    assert entries == []

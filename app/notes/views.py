"""
Contains view functions for notes blueprint.
"""

from flask import (
    Blueprint, render_template, current_app, request, jsonify, make_response, abort, send_from_directory, redirect,
    url_for, flash
)
from flask.wrappers import Response
from marshmallow.exceptions import ValidationError
from flask_login import current_user

from .messages import (NO_DATA_TO_ADD, MISSING_JSON, NOTE_DOES_NOT_EXIST, ENTRY_DOES_NOT_EXIST, FIRST_NOTE_CREATED)
from .models import Note, Entry
from .shemas import entry_schema, entries_schema, note_schema, notes_schema
from .forms import AddFirstNoteForm
from ..accounts.utils import redirect_to_last_updated_note


notes_blueprint = Blueprint('notes', __name__, template_folder='templates')


@notes_blueprint.route('/notes/<note_id>', methods=['GET'])
def note(note_id: int) -> str:
    """The view renders single note page."""
    note = Note.get_by_id(note_id)  # pylint: disable=redefined-outer-name
    if not note or note.user_id != current_user.id:
        abort(404)
    number_of_notes = Note.count_user_notes(current_user.id)
    return render_template('notes/note.html', note=note, number_of_notes=number_of_notes)


@notes_blueprint.route('/notes/<note_id>/export', methods=['GET'])
def note_export(note_id: int) -> str:
    """The view renders note export page where user can download note as pdf."""
    note = Note.get_by_id(note_id)  # pylint: disable=redefined-outer-name
    if not note or note.user_id != current_user.id:
        abort(404)
    number_of_notes = Note.count_user_notes(current_user.id)
    return render_template('notes/export_note.html', note=note, number_of_notes=number_of_notes)


@notes_blueprint.route('/note/first', methods=['GET', 'POST'])
def add_first_note():
    """The view renders page to add first note."""
    number_of_notes = Note.count_user_notes(current_user.id)
    if number_of_notes:
        return redirect_to_last_updated_note()
    form = AddFirstNoteForm()
    if form.validate_on_submit():
        note = Note(title=form.title.data,  # pylint: disable=redefined-outer-name
                    description=form.description.data,
                    user_id=current_user.id)
        note.save_to_db()
        flash(FIRST_NOTE_CREATED, 'error')
        return redirect(url_for('notes.note', note_id=note.id))
    return render_template('notes/add_first_note.html', form=form)


@notes_blueprint.route('/media/notes/img/<year>/<month>/<day>/<filename>')
def media_notes_img(year: str, month: str, day: str, filename: str) -> Response:
    """The view returns note image."""
    image_path = current_app.config['MEDIA_ROOT'] / 'notes' / 'img' / year / month / day
    return send_from_directory(image_path, filename)


@notes_blueprint.route('/media/notes/pdf/<filename>')
def media_notes_pdf(filename: str) -> Response:
    """The view returns note pdf file."""
    return send_from_directory(current_app.config['MEDIA_NOTES_PDF'], filename, as_attachment=True)


@notes_blueprint.route('/api/notes', methods=['GET'])
def load_notes() -> Response:
    """The view returns list of notes as json object."""
    page = request.args.get('npage', 1, type=int)
    pagination = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated.desc()).paginate(
        page,
        per_page=current_app.config['NOTES_PER_PAGE'],
        error_out=False
    )
    notes = notes_schema.dump(pagination.items)
    response_content = {
        'notes': notes,
        'has_next': pagination.has_next,
        'next_num': pagination.next_num
    }
    return make_response(jsonify(response_content), 200)


@notes_blueprint.route('/api/notes', methods=['POST'])
def add_note() -> Response:
    """The view addes new note."""
    if request.is_json:
        data = request.get_json()
        if data:
            try:
                note = note_schema.load(data)  # pylint: disable=redefined-outer-name
                note.user_id = current_user.id
                saved_note = note.save_to_db()
            except ValidationError as error:
                return make_response(jsonify({'error': error.messages}), 400)
            return make_response(jsonify({'note': note_schema.dump(saved_note)}), 200)
        return make_response(jsonify({'error': NO_DATA_TO_ADD}), 400)
    return make_response(jsonify({'error': MISSING_JSON}), 400)


@notes_blueprint.route('/api/notes/<note_id>/entries', methods=['GET'])
def load_entries(note_id: int) -> Response:
    """The view returns list of entries as json object."""
    if not Entry.get_by_note_id(note_id):
        return make_response(jsonify({'error': 'No entries.'}), 200)
    page = request.args.get('epage', 1, type=int)
    pagination = Entry.query.filter_by(note_id=note_id).order_by(Entry.created.desc()).paginate(
        page,
        per_page=current_app.config['ENTRIES_PER_PAGE'],
        error_out=False
    )
    entries = entries_schema.dump(pagination.items)
    response_content = {
        'entries': entries,
        'has_next': pagination.has_next,
        'next_num': pagination.next_num
    }
    return make_response(jsonify(response_content), 200)


@notes_blueprint.route('/api/notes/<note_id>/entries', methods=['POST'])
def add_entry(note_id: int) -> Response:
    """The view addes new entry."""
    if not Note.get_by_id(note_id):
        return make_response(jsonify({'error': NOTE_DOES_NOT_EXIST}), 404)
    if request.is_json:
        data = request.get_json()
        if data:
            try:
                entry = entry_schema.load(data)
            except ValidationError as error:
                return make_response(jsonify({'error': error.messages}), 400)
            entry.note_id = note_id
            saved_entry = entry.save_to_db()
            return make_response(jsonify({'entry': entry_schema.dump(saved_entry)}), 200)
        return make_response(jsonify({'error': NO_DATA_TO_ADD}), 400)
    return make_response(jsonify({'error': MISSING_JSON}), 400)


@notes_blueprint.route('/api/notes/<note_id>/entries/<entry_id>', methods=['PUT'])
def update_entry(note_id: int, entry_id: int) -> Response:
    """The view updates entry."""
    if not Note.get_by_id(note_id):
        return make_response(jsonify({'error': NOTE_DOES_NOT_EXIST}), 404)
    entry = Entry.get_by_id(entry_id)
    if entry and int(entry.note_id) == int(note_id):
        if request.is_json:
            data = request.get_json()
            if data:
                try:
                    validated_entry_data = entry_schema.load(data, partial=True)
                except ValidationError as error:
                    return make_response(jsonify({'error': error.messages}), 400)
                entry.content = validated_entry_data.content  # add update of note_id
                saved_entry = entry.save_to_db()
                return make_response(jsonify({'entry': entry_schema.dump(saved_entry)}), 200)
            return make_response(jsonify({'error': NO_DATA_TO_ADD}), 400)
        return make_response(jsonify({'error': MISSING_JSON}), 400)
    return make_response(jsonify({'error': ENTRY_DOES_NOT_EXIST}), 404)


@notes_blueprint.route('/api/notes/<note_id>/entries/<entry_id>', methods=['DELETE'])
def delete_entry(note_id: int, entry_id: int) -> Response:
    """The view deletes entry."""
    if not Note.get_by_id(note_id):
        return make_response(jsonify({'error': NOTE_DOES_NOT_EXIST}), 404)
    entry = Entry.get_by_id(entry_id)
    if entry:
        response = {'entry': entry_schema.dump(entry)}
        entry.delete_from_db()
        return make_response(jsonify(response), 200)
    return make_response(jsonify({'error': ENTRY_DOES_NOT_EXIST}), 404)


@notes_blueprint.route('/api/notes/<note_id>/export/pdf', methods=['GET'])
def note_export_pdf(note_id: int) -> str:
    """The view generates note pdf."""
    note = Note.get_by_id(note_id)  # pylint: disable=redefined-outer-name
    if not note:
        return make_response(jsonify({'error': NOTE_DOES_NOT_EXIST}), 404)
    from .tasks import generate_note_pdf  # pylint: disable=import-outside-toplevel
    result = generate_note_pdf.delay(note.id)
    return make_response(jsonify({'report_status': 'started', 'task_id': result.id}), 200)


@notes_blueprint.route('/api/task/<task_id>', methods=['GET'])
def task_progress(task_id: str) -> str:
    """The view shows background task progress."""
    from .tasks import generate_note_pdf  # pylint: disable=import-outside-toplevel
    task = generate_note_pdf.AsyncResult(task_id)
    status = task.status
    progress = 0
    result = ''
    if status == 'SUCCESS':
        progress = 100
        result = task.result
    elif status == 'FAILURE':
        progress = 0
    elif status == 'PROGRESS':
        progress = task.info.get('current')
    else:
        status = 'PROGRESS'
    response = {'progress': progress, 'status': status}
    if result:
        response['result'] = f'/media/notes/pdf/{result}'
    return make_response(jsonify(response), 200)

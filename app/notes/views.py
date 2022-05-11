import json
from flask import (
    Blueprint, render_template, current_app, request, jsonify, make_response, abort, request, send_from_directory
)
from flask.wrappers import Response
from marshmallow.exceptions import ValidationError

from .models import Note, Entry
from .shemas import entry_schema, entries_schema, note_schema, notes_schema


notes_blueprint = Blueprint('notes',
                            __name__,
                            template_folder='templates')


@notes_blueprint.route('/notes/<note_id>', methods=['GET'])
def note(note_id: int) -> str:
    note = Note.get_by_id(note_id)
    if not note:
        abort(404)
    number_of_notes = Note.count()
    return render_template('notes/note.html', note=note, number_of_notes=number_of_notes)


@notes_blueprint.route('/api/notes', methods=['GET'])
def load_notes() -> Response:
    page = request.args.get('npage', 1, type=int)
    pagination = Note.query.order_by(Note.updated.desc()).paginate(
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
    if request.is_json:
        data = request.get_json()
        if data:
            try:
                note = note_schema.load(data)
                saved_note = note.save_to_db()
            except ValidationError as error:
                return make_response(jsonify({'error': error.messages}), 200)
            return make_response(jsonify({'note': note_schema.dump(saved_note)}), 200)
        else:
            return make_response(jsonify({'error': 'no data to add'}), 200)
    return make_response(jsonify({'error': 'json data is required'}), 200)


@notes_blueprint.route('/api/notes/<note_id>/entries', methods=['GET'])
def load_entries(note_id: int) -> Response:
    if not Entry.get_by_note_id(note_id):
        abort(404)
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
    if not Note.get_by_id(note_id):
        abort(404)
    if request.is_json:
        data = request.get_json()
        if data:
            try:
                entry = entry_schema.load(data)
            except ValidationError as error:
                return make_response(jsonify({'error': error.messages}), 200)
            entry.note_id = note_id
            saved_entry = entry.save_to_db()
            return make_response(jsonify({'entry': entry_schema.dump(saved_entry)}), 200)
        else:
            return make_response(jsonify({'error': 'no data to add'}), 200)
    return make_response(jsonify({'error': 'json data is required'}), 200)


@notes_blueprint.route('/api/notes/<note_id>/entries/<entry_id>', methods=['DELETE'])
def delete_entry(note_id: int, entry_id: int) -> Response:
    if not Note.get_by_id(note_id):
        abort(404)
    entry = Entry.get_by_id(entry_id)
    if entry:
        response = {'entry': entry_schema.dump(entry)}
        entry.delete_from_db()
        return make_response(jsonify(response), 200)
    return make_response(jsonify({'error': 'Entry doesnot exist'}), 404)


@notes_blueprint.route('/media/<filename>')
def media(filename):
    return send_from_directory(current_app.config['MEDIA_ROOT'], filename)

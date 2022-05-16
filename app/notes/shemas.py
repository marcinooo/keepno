"""Contains shemas."""

from marshmallow_sqlalchemy import auto_field, fields
from marshmallow import pre_load, post_load, ValidationError

from ..app import ma
from .models import Entry, Note


class NoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Note
        include_relationships = True
        load_instance = True

    id = auto_field()
    title = auto_field()
    description = auto_field()
    created = fields.fields.DateTime(format='iso')
    updated = fields.fields.DateTime(format='iso')

    @post_load
    def require_not_empty_title(self, note: Note, **kwargs) -> Note:
        if not note.title:
            raise ValidationError('Note must have title.', 'title')
        return note


class EntrySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Entry
        include_relationships = True
        load_instance = True

    id = auto_field()
    content = auto_field()
    note_id = auto_field()
    created = fields.fields.DateTime(format='iso')
    updated = fields.fields.DateTime(format='iso')

    @post_load
    def require_not_empty_content(self, entry: Entry, **kwargs) -> Entry:
        if not entry.content:
            raise ValidationError('Entry must have content.', 'content')
        return entry


entry_schema = EntrySchema()
entries_schema = EntrySchema(many=True)

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

"""
Contains shemas for notes models.
"""

from marshmallow_sqlalchemy import auto_field, fields
from marshmallow import post_load, ValidationError

from ..app import ma
from .models import Entry, Note


class NoteSchema(ma.SQLAlchemySchema):
    """Creates schema for Note model."""

    class Meta:  # pylint: disable=too-few-public-methods,missing-class-docstring
        model = Note
        include_relationships = True
        load_instance = True

    id = auto_field()
    title = auto_field()
    description = auto_field()
    created = fields.fields.DateTime(format='iso')
    updated = fields.fields.DateTime(format='iso')

    @post_load
    def require_not_empty_title(self, note: Note, **_) -> Note:  # pylint: disable=no-self-use
        """Checks if title is not empty."""
        if not note.title:
            raise ValidationError('Note must have title.', 'title')
        return note


class EntrySchema(ma.SQLAlchemySchema):
    """Creates schema for Entry model."""

    class Meta:  # pylint: disable=too-few-public-methods,missing-class-docstring
        model = Entry
        include_relationships = True
        load_instance = True

    id = auto_field()
    content = auto_field()
    note_id = auto_field()
    created = fields.fields.DateTime(format='iso')
    updated = fields.fields.DateTime(format='iso')

    @post_load
    def require_not_empty_content(self, entry: Entry, **_) -> Entry:  # pylint: disable=no-self-use
        """Checks if entry is not empty."""
        if not entry.content:
            raise ValidationError('Entry must have content.', 'content')
        return entry


entry_schema = EntrySchema()
entries_schema = EntrySchema(many=True)

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

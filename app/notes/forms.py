"""
Contains forms to render in notes blueprint templates.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class AddFirstNoteForm(FlaskForm):
    """Form adds first Note."""

    title = StringField(
        'Title',
        validators=[
            DataRequired('This field is required.'),
            Length(min=3, max=50),
        ]
    )

    description = StringField(
        'Description',
        validators=[
            DataRequired('This field is required.'),
            Length(min=5, max=100),
        ]
    )

    submit = SubmitField(
        'Add note'
    )

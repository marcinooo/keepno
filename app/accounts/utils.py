"""
Contains various utils for accounts blueprint.
"""

import re
import uuid
from typing import Tuple
from pathlib import Path
from functools import wraps
from wtforms.validators import ValidationError
from wtforms import PasswordField, StringField
from flask import current_app, url_for, redirect
from flask.wrappers import Response
from flask_login import current_user
from werkzeug.datastructures import FileStorage
from PIL import Image

from ..app import login_manager
from .models import User
from ..notes.models import Note


class PasswordType:  # pylint: disable=too-few-public-methods
    """
    Creates validator for password field. The validator checks if the password contains at least one letter,
    at least one number, and at least one capital letter.
    """

    def __init__(self, missing_number_message: str, missing_letter_message: str, missing_capital_letter_message: str):
        self.missing_number_message = missing_number_message
        self.missing_letter_message = missing_letter_message
        self.missing_capital_letter_message = missing_capital_letter_message

    def __call__(self, _, field: PasswordField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        password = field.data
        if re.search('[0-9]', password) is None:
            raise ValidationError(self.missing_number_message)
        if re.search('[a-z]', password) is None:
            raise ValidationError(self.missing_letter_message)
        if re.search('[A-Z]', password) is None:
            raise ValidationError(self.missing_capital_letter_message)


class PasswordOfCurrentUser:  # pylint: disable=too-few-public-methods
    """
    Creates validator for password field. The validator checks if the password belongs to current logged user.
    """

    def __init__(self, message: str):
        self.message = message

    def __call__(self, _, field: PasswordField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        password = field.data
        if not current_user.check_password(password):
            raise ValidationError(self.message)


class DeleteSlug:  # pylint: disable=too-few-public-methods
    """
    Creates validator for string field. The validator checks if the passed value equals to required constant value.
    """

    def __init__(self, message: str, required_slug: str):
        self.message = message
        self.required_slug = required_slug

    def __call__(self, _, field: StringField):
        """Raises ValidationError if the required conditions are not met."""
        slug = field.data
        if slug != self.required_slug:
            raise ValidationError(self.message)


class UniqueEmail:  # pylint: disable=too-few-public-methods
    """
    Class creates validator for email form field. Validator checks that the email is unique.
    """

    def __init__(self, message: str, skip_current_user: bool = True):
        self.message = message
        self.skip_current_user = skip_current_user

    def __call__(self, _, field: StringField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        email = field.data
        user = User.find_by_email(email)
        if user:
            if self.skip_current_user:
                if user.email != current_user.email:
                    raise ValidationError(self.message)
            else:
                raise ValidationError(self.message)


class UniqueUsername:  # pylint: disable=too-few-public-methods
    """
    Class creates validator for username form field. Validator checks that the username is unique.
    """

    def __init__(self, message: str, skip_current_user: bool = True):
        self.message = message
        self.skip_current_user = skip_current_user

    def __call__(self, _, field: StringField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        username = field.data
        user = User.find_by_username(username)
        if user:
            if self.skip_current_user:
                if user.username != current_user.username:
                    raise ValidationError(self.message)
            else:
                raise ValidationError(self.message)


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """
    Assigns a user object to the global current_user variable.
    :param user_id: id of user to assigne
    :return: User instance
    """
    return User.find_by_id(user_id)


def redirect_authenticated_users(func):  # add function annotation
    """
    The decorator redirects authenticated users to note view.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect_to_last_updated_note()
        return func(*args, **kwargs)
    return wrapper


def active_account_required(func):
    """
    The decorator redirects authenticated and inactive users to unconfirmed view.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and not current_user.active:
            return redirect(url_for('accounts.unconfirmed'))
        return func(*args, **kwargs)
    return wrapper


def save_picture(form_picture: FileStorage, output_size:  Tuple[int, int] = (125, 125)) -> str:
    """
    Saves user avatar in media directory.
    :param form_picture: form file field
    :return: unique filename
    """
    hex_name = uuid.uuid4().hex
    f_ext = Path(form_picture.filename).suffix
    filename = hex_name + f_ext
    picture_path = current_app.config['MEDIA_ROOT'] / 'accounts' / 'img' / filename
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    return filename


def redirect_to_last_updated_note() -> Response:
    """
    Redirects user to last edited note.
    :return: redirection
    """
    last_edited_note = Note.get_last_edited_note()
    return redirect(url_for('notes.note', note_id=last_edited_note.id))

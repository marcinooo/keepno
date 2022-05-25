"""
Contains forms to render in accounts blueprint templates.
"""

from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from .utils import PasswordType, UniqueEmail, UniqueUsername, PasswordOfCurrentUser, DeleteSlug


class RegistrationForm(FlaskForm):
    """Form get user data during registration."""

    username = StringField(
        'Username',
        validators=[
            DataRequired('This field is required.'),
            Length(min=3, max=50),
            UniqueUsername('This username is already taken.'),
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired('This field is required.'),
            Length(min=5, max=100),
            Email(),
            UniqueEmail('This email is already taken, please select another one.'),
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired('This field is required.'),
            Length(min=6, max=100),
            PasswordType(
                'Make sure your password has a number in it.',
                'Make sure your password has a letter in it.',
                'Make sure your password has a capital letter in it.'
            ),
        ]
    )

    confirm_password = PasswordField(
        'Password confirmation',
        validators=[
            DataRequired('This field is required.'),
            EqualTo('password'),
        ]
    )

    recaptcha = RecaptchaField()

    submit = SubmitField(
        'Register'
    )


class LoginForm(FlaskForm):
    """Form get user credentials during authentication."""

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
        ]
    )

    remember = BooleanField(
        'Remember me'
    )

    submit = SubmitField(
        'Log in'
    )


class AccountUpdateForm(FlaskForm):
    """Form get user data while updating information about him."""

    username = StringField(
        'Username',
        validators=[
            Length(min=3, max=50),
            UniqueUsername('This username is already taken.'),
        ]
    )

    email = StringField(
        'Email',
        validators=[
            Length(min=5, max=100),
            Email(),
            UniqueEmail('This email is already taken, please select another one.'),
        ]
    )

    description = StringField(
        'Description',
    )

    image = FileField(
        'Image',
        validators=[
            FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')
        ]
    )

    use_gravatar = BooleanField(
        'Use gravatar'
    )

    submit = SubmitField(
        'Update'
    )


class ChangePasswordForm(FlaskForm):
    """Form get new password."""

    old_password = PasswordField(
        'Current password',
        validators=[
            DataRequired('This field is required.'),
            PasswordOfCurrentUser('Invalid current password.'),
        ]
    )

    new_password = PasswordField(
        'New password',
        validators=[
            DataRequired('This field is required.'),
            Length(min=6, max=100),
            PasswordType(
                'Make sure your password has a number in it.',
                'Make sure your password has a letter in it.',
                'Make sure your password has a capital letter in it.'
            ),
        ]
    )

    confirm_new_password = PasswordField(
        'New password confirmation',
        validators=[
            DataRequired('This field is required.'),
            EqualTo('new_password'),
        ]
    )

    submit = SubmitField(
        'Change'
    )


class DeleteAccountForm(FlaskForm):
    """Form get confirmation slug during deletions account."""

    REQUIRED_SLUG = 'delete'

    slug = StringField(
        'Confirm deletion',
        validators=[
            DeleteSlug(f'Invalid slug. Please type "{REQUIRED_SLUG}" to delete your account.', REQUIRED_SLUG),
        ]
    )

    submit = SubmitField(
        'Delete'
    )


class ResetPasswordEmailInputForm(FlaskForm):
    """Form get email to send reset password mali."""

    email = StringField(
        'Email',
        validators=[
            DataRequired('This field is required.'),
            Email(),
        ]
    )

    recaptcha = RecaptchaField()

    submit = SubmitField(
        'Send'
    )


class ResetPasswordNewPasswordInputForm(FlaskForm):
    """Form get new password."""

    password = PasswordField(
        'Password',
        validators=[
            DataRequired('This field is required.'),
            Length(min=6, max=100),
            PasswordType(
                'Make sure your password has a number in it.',
                'Make sure your password has a letter in it.',
                'Make sure your password has a capital letter in it.'
            ),
        ]
    )

    confirm_password = PasswordField(
        'Password confirmation',
        validators=[
            DataRequired('This field is required.'),
            EqualTo('password'),
        ]
    )

    submit = SubmitField(
        'Set'
    )

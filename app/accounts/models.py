"""
Contains models for accounts blueprint.
"""
# pylint: disable=no-member

import time
import datetime
import hashlib
import jwt
from flask import current_app, request, url_for
from sqlalchemy.ext.declarative import declared_attr
from flask_login import UserMixin

from ..app import db, bcrypt


class BaseMixin:
    """Base class which is common for other models."""

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

    def save_to_db(self) -> None:
        """Saves model to database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """Deletes model from database."""
        db.session.delete(self)
        db.session.commit()


class User(UserMixin, BaseMixin, db.Model):
    """
    Creates object which is representation of app user.
    """
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean(), default=False)
    profile = db.relationship('Profile', uselist=False, backref="user", cascade="all, delete")

    def check_password(self, password: str) -> bool:
        """
        Checks if the passed password matches the user's password.
        :param password: password to check
        :return: True if passwords match, otherwise False
        """
        return bcrypt.check_password_hash(self.password, password)

    def generate_jwt_token(self, expire_time: int = 600) -> str:
        """
        Creates jwt token which is valid in given time.
        :param expire_time: time to expire token
        :return: jwt token
        """
        return jwt.encode(
            {'user_id': self.id, 'exp': time.time() + expire_time},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    def change_email(self, email: str) -> None:
        """
        Changes user email.
        :param email: new user email
        :return: None
        """
        self.email = email
        if self.profile:
            self.profile.generate_gravatar_url()
            self.profile.save_to_db()

    @classmethod
    def find_by_id(cls, _id: int) -> 'User':
        """
        Returns user based on the given user id.
        :param _id: user id
        :return: user with the given id or None
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_username(cls, username: str) -> 'User':
        """
        Returns user based on the given user username.
        :param _id: username
        :return: user with the given username or None
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> 'User':
        """
        Returns user based on the given user email.
        :param _id: user's email
        :return: user with the given email or None
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def generate_password_hash(cls, password: str) -> str:
        """
        Generates hash for given password.
        :param password: password
        :return: password's hash
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @classmethod
    def verify_jwt_token(cls, token: str) -> 'User':
        """
        Validates jwt token.
        :param token: token
        :return: founded user, otherwise None
        """
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
        except Exception:  # pylint: disable=broad-except
            return None
        return User.query.get(user_id)

    def __repr__(self):
        """
        Returns user representation.
        :return: user string representation
        """
        return f"User('{self.email}')"


class Profile(BaseMixin, db.Model):
    """
    Creates object which is representation of profile for user.
    """
    __tablename__ = 'profiles'

    gravatar_url = db.Column(db.String())
    image = db.Column(db.String())
    custom_image = db.Column(db.Boolean(), default=False)
    description = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def user_image(self) -> str:
        """
        Returns url for user's avatar (it can be custom image or gravatar).
        :return: image url
        """
        return url_for('accounts.media_user_img', filename=self.image) if self.custom_image else self.gravatar_url

    def generate_gravatar_url(self, size: int = 600, default: str = 'retro', rating: str = 'g') -> str:
        """
        Prepares gravatar url based on user email.
        :param size: image size
        :param default: image type
        :param rating: suitable for display on all websites
        :return: ready url
        """
        email = self.user.email
        url = 'http://www.gravatar.com/avatar'
        with current_app.test_request_context():
            if request.is_secure:
                url = 'https://secure.gravatar.com/avatar'
        md5_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
        url = f'{url}/{md5_hash}?s={size}&d={default}&r={rating}'
        self.gravatar_url = url
        return url

    def __repr__(self):
        """
        Returns profile representation.
        :return: profile string representation
        """
        return f"Profile('{self.user.email}')"

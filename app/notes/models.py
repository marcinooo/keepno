"""
The script contains models for account blueprint.
"""

import datetime
from sqlalchemy.ext.declarative import declared_attr

from ..app import db


class BaseMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

    def save_to_db(self) -> None:
        """The method saves model to db."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete_from_db(self) -> None:
        """The method deletes model from db."""
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class Note(BaseMixin, db.Model):
    __tablename__ = 'notes'
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(240))
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    @classmethod
    def count(cls):
        return cls.query.count()


class Entry(BaseMixin, db.Model):
    __tablename__ = 'entries'
    content = db.Column(db.String(1000), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    @classmethod
    def get_by_note_id(cls, _id):
        return cls.query.filter_by(note_id=_id).all()

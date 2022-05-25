"""Contains models for database."""

from __future__ import annotations

import uuid
import base64
import datetime
from typing import List
from pathlib import Path
from bs4 import BeautifulSoup
from flask import current_app

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates, reconstructor
from sqlalchemy import and_

from ..app import db


class BaseMixin(object):
    """Contains methods for all models."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

    def save_to_db(self) -> BaseMixin:
        """Saves model to database."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete_from_db(self) -> BaseMixin:
        """Deletes model from database."""
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get_all(cls) -> List[BaseMixin]:
        """Gets all objects from database."""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, _id) -> BaseMixin:
        """Gets single object by id from database."""
        return cls.query.filter_by(id=_id).first()


class Note(BaseMixin, db.Model):
    """Creates note object."""
    __tablename__ = 'notes'
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(240))
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    pdf_note = db.relationship('PdfNote', uselist=False, backref="note", cascade="all, delete")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @classmethod
    def get_last_edited_note(cls):
        return  cls.query.order_by(cls.updated.desc()).limit(1).first()

    @classmethod
    def count_all(cls) -> int:
        """Counts all objects in database."""
        return cls.query.count()

    @classmethod
    def count_user_notes(cls, user_id) -> int:
        """Counts all objects in database."""
        return cls.query.filter_by(user_id=user_id).count()


class Entry(BaseMixin, db.Model):
    """Creates entry object."""
    __tablename__ = 'entries'
    content = db.Column(db.Text(), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, **kwargs) -> None:
        self._content_images_to_save = []
        self._content_images_to_delete = []
        super(Entry, self).__init__(**kwargs)

    @reconstructor
    def init_on_load(self):
        self._content_images_to_save = []
        self._content_images_to_delete = []

    @classmethod
    def get_by_note_id(cls, _id: int) -> List[Entry]:
        """Gets single object by related entry id from database."""
        return cls.query.filter_by(note_id=_id).all()

    @classmethod
    def get_by_note_id_in_order_of_creation(cls, _id: int) -> List[Entry]:
        """."""
        return cls.query.filter_by(note_id=_id).order_by(Entry.updated.desc()).all()

    @classmethod
    def count_for_given_note_id(cls, _id: int) -> int:
        """Counts all objects in database for given note id."""
        return cls.query.filter_by(note_id=_id).count()
    
    def save_to_db(self) -> Entry:
        """Saves object to database."""
        super().save_to_db()
        self.content = self._validate_content_before_saving()
        if self._content_images_to_save:
            for image in self._content_images_to_save:
                image.save()
        if self._content_images_to_delete:
            for image in self._content_images_to_delete:
                image.delete()
        self._content_images_to_save = []
        self._content_images_to_delete = []
        return self

    def delete_from_db(self) -> Entry:
        """Deletes model from database."""
        content_images = EntryContentImage.get_by_entry_id(self.id)
        for image in content_images:
            image.delete()
        super().delete_from_db()
        return self

    def _validate_content_before_saving(self) -> str:
        """Finds all images passed as base64 string in entry content and saves it in local os."""
        soup = BeautifulSoup(self.content)
        already_saved_content_images_ids = []
        for img in soup.findAll('img'):
            src = img['src']
            if 'data:image/png;base64' in src:
                id_ = uuid.uuid4().hex
                name = id_ + '.png'
                current_date = datetime.datetime.utcnow().date()
                path = f'notes/img/{current_date.year}/{current_date.month}/{current_date.day}'
                entry_content_image = EntryContentImage(
                    base64_string=src[22:].encode('utf-8'), path=path, name=name, entry_id=self.id
                )
                self._content_images_to_save.append(entry_content_image)
                img['src'] = f'/media/{path}/{name}'
                img['id'] = id_
            elif '/media/' in src:
                name = Path(src).name
                entry_content_image = EntryContentImage.get_by_name(name)
                if entry_content_image:
                    already_saved_content_images_ids.append(entry_content_image.id)
        self._content_images_to_delete = EntryContentImage.get_by_ids_which_are_not_in(
            self.id, already_saved_content_images_ids
        )
        return str(soup)


class EntryContentImage(BaseMixin, db.Model):
    """Creates object which represents image from entry content."""
    __tablename__ = 'entrycontentimages'
    name = db.Column(db.String(50), nullable=False)  # add unique
    path = db.Column(db.String(50), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'), nullable=False)

    def __init__(self, base64_string: str = '', **kwargs) -> None:
        super(EntryContentImage, self).__init__(**kwargs)
        self.base64_string = base64_string

    @classmethod
    def get_by_name(cls, name: str) -> EntryContentImage:
        """Gets single object by name from database."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_by_ids_which_are_not_in(cls, _id: int, ids: List[int]) -> List[EntryContentImage]:
        """Gets all objects with id not on the passed list."""
        entry_content_images = cls.query.filter(
            and_(EntryContentImage.id.notin_(ids), EntryContentImage.entry_id == _id)
        ).all()
        return entry_content_images

    @classmethod
    def get_by_entry_id(cls, _id: int) -> List[EntryContentImage]:
        """Gets single object by related entry id from database."""
        return cls.query.filter_by(entry_id=_id).all()

    def save(self) -> EntryContentImage:
        """Saves object to database and image in local os."""
        self.create_image_directory()
        self.dump_base64_string_to_image(path=self.get_image_path())
        self.save_to_db()
        return self

    def delete(self) -> EntryContentImage:
        """Deletes object from database and image form local os."""
        image_to_remove = self.get_image_path()
        image_to_remove.unlink()
        self.delete_from_db()
        return self

    def dump_base64_string_to_image(self, path: Path) -> None:
        """Saves image in local os."""
        if not self.base64_string:
            raise TypeError('base64_string is needed to save image')
        with open(path, "wb") as fh:
            fh.write(base64.decodebytes(self.base64_string))

    def get_image_path(self) -> Path:
        """Returns path to image in local os."""
        return Path(current_app.config['MEDIA_ROOT']) / self.path / self.name

    def create_image_directory(self):
        path = current_app.config['MEDIA_ROOT'] / self.path
        path.mkdir(parents=True, exist_ok=True)


class PdfNote(BaseMixin, db.Model):
    """Creates pdf note object."""
    __tablename__ = 'pdfnotes'
    pdf_name = db.Column(db.String(100), unique=True, nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # wywal to
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'))

    def refresh_creation_date(self):
        self.created = datetime.datetime.utcnow()
        self.save_to_db()

    @classmethod
    def get_by_pdf_name(cls, pdf_name: str) -> PdfNote:
        """Gets single object by pdf name from database."""
        return cls.query.filter_by(pdf_name=pdf_name).first()

    @classmethod
    def get_by_note_id(cls, _id: int) -> PdfNote:
        """Gets single object by related note id from database."""
        return cls.query.filter_by(note_id=_id).first()

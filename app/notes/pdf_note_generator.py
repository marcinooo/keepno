"""Contains code to generate pdf for single note."""

import pdfkit
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template
from flask import current_app
from bs4 import BeautifulSoup

from .models import Note, Entry
from .shemas import entry_schema


class PdfNoteGenerator:
    """Creates pdf generator for note data."""

    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'footer-center': '[page]'
    }

    def __init__(self, note_template_path: str, entry_template_path: str, search_path: str):
        self.note_template_path = note_template_path
        self.entry_template_path = entry_template_path
        self.search_path = search_path
        self._environment = self._get_environment(search_path)
        self._template = None

    def add_header(self, note: Note) -> None:
        """
        Dumps note data to output file.
        :param note: note with title and short description attributes to dump in pdf
        :return: None
        """
        self._template = self._environment.get_template(self.note_template_path)
        self._template = self._render_template({'note': note})

    def add_entry(self, entry: Entry) -> None:
        """
        Dumps entry data to output file.
        :param entry: entry with content and date of creations (created) attributes to dump in pdf
        :return: None
        """
        if self._template is None:
            raise Exception('Header is not added')
        entry_template = self._environment.get_template(self.entry_template_path)
        filled_entry_template = entry_template.render({'entry': self._dump_entry(entry)})
        self._template = self._render_template({'entry_template': filled_entry_template})

    def render(self, name: str) -> None:
        """
        Dumps prepared template to file.
        :param name: name of file to save
        :return: None
        """
        if self._template is None:
            raise Exception('Header is not added')
        self._template = self._render_template({'entry_template': ''})
        prepared_template = self._template.render()
        with open('test.html', 'w') as fd:
            fd.write(prepared_template)
        pdfkit.from_string(prepared_template, name, self.options)

    def _render_template(self, context: dict) -> Template:
        """
        Creates new tempate object from string in `self._template`.
        :param context: data to dump
        :return: new template (ready to dump)
        """
        return Template(self._template.render(context))

    @staticmethod
    def _get_environment(search_path: str) -> Environment:
        """
        Creates environment for templates searching.
        :param search_path: path to directory with templates
        :return: new environment
        """
        file_loader = FileSystemLoader(search_path)
        return Environment(loader=file_loader, undefined=DebugUndefined)

    def _dump_entry(self, entry: Entry) -> dict:
        """
        Dumps Entry object to dict and replace all paths in src attribute of entry content.
        :param entry: Entry object
        :return: entry as dict
        """
        entry = entry_schema.dump(entry)
        soup = BeautifulSoup(entry['content'])
        for img in soup.findAll('img'):
            src = img['src']
            image_path = '/'.join(src.split('/')[2:])
            new_img_src = current_app.config['MEDIA_ROOT'] / image_path
            img['src'] = new_img_src
        entry['content'] = str(soup)
        return entry

"""Contains long tasks."""

import time
import uuid
from pathlib import Path
from flask import current_app

from ..celery import celery
from .models import Note, Entry, PdfNote
from .pdf_note_generator import PdfNoteGenerator


@celery.task(bind=True)
def generate_note_pdf(task, note_id):
    """
    Runs task to generate pdf note in backgroud.
    :param task: celery test
    :param note_id: id of note
    :return: task's result
    """
    task = PdfNoteGeneratorTask(task)
    task.run(note_id)
    return task.result


class PdfNoteGeneratorTask:
    """Class creates object which generates new pdf note file and notices progress of generation."""

    def __init__(self, task):
        self.task = task
        self.pdf_note_generator = PdfNoteGenerator(
            'note.html', 'entry.html', self._get_templates_path()
        )
        self.result = None

    def run(self, note_id: int) -> None:
        """
        Generates new pdf note file. Regularly updates the file generation progress.
        :param note_id: id of related note
        :return: None
        """
        if self._check_if_pdf_note_exists(note_id):
            return
        progress = 0
        self._update_task_progress(progress)
        number_of_entries = Entry.count_for_given_note_id(note_id)
        note = Note.get_by_id(note_id)
        self.pdf_note_generator.add_header(note)
        progress_step = self._calculate_progress_step(number_of_entries)
        progress += progress_step
        self._update_task_progress(progress)
        entries = Entry.get_by_note_id_in_order_of_creation(note_id)
        for entry in entries:
            self.pdf_note_generator.add_entry(entry)
            progress += progress_step
            self._update_task_progress(progress)
        filename = self._get_pdf_note_filename()
        filepath =  Path(current_app.config['MEDIA_ROOT']) / 'notes' / 'pdf' / filename
        self.pdf_note_generator.render(filepath)
        self._update_task_progress(100)
        self._create_pdf_note_in_database(filename, note_id)
        self.result = filename

    def _update_task_progress(self, percentage: int) -> None:
        """
        Sets the percentage of progress for task.
        :percentage: percentage to set
        :return: None
        """
        self.task.update_state(state='PROGRESS', meta={'current': percentage})

    def _get_pdf_note_filename(self) -> str:
        """
        Creates name for new pdf note.
        :return: pdf name 
        """
        return uuid.uuid4().hex + '.pdf'

    def _get_templates_path(self) -> Path:
        """
        Creates path to directory with pdf templates.
        :return: prepared path 
        """
        return Path(current_app.config['BASEDIR']) / 'app' / 'notes' / 'templates' / 'pdf'

    def _calculate_progress_step(self, number_of_entries: int) -> int:
        """
        Calculates number of progress updates during task execution.
        :param number_of_entries: number of entries for given note
        :return: calculated step
        """
        steps = 2 + number_of_entries
        step = int(100 / steps)
        return step

    def _create_pdf_note_in_database(self, pdf_name: str, note_id: int) -> None:
        """
        Cretes new pdf note object in database. Old is deleted if exists.
        :param pdf_name: name of generated pdf_file
        :param note_id: id of related note
        :return: None
        """
        pdf_note = PdfNote.get_by_pdf_name(pdf_name)
        if pdf_note:
            pdf_note.delete_from_db()  # add deletions of files
        new_pdf_note = PdfNote(pdf_name=pdf_name, note_id=note_id)
        new_pdf_note.save_to_db()

    def _check_if_pdf_note_exists(self, note_id: int) -> None:
        """
        Checks if pdf note file exists and if it is not outdated.
        :param note_id: id of note related with pdf file
        :return: True if file exists and is not outdated
        """
        pdf_note = PdfNote.get_by_note_id(note_id)
        if not pdf_note:
            return False
        if pdf_note.note.updated > pdf_note.created:
            return False
        entries = Entry.get_by_note_id(note_id)
        for entry in entries:
            if entry.updated > pdf_note.created:
                return False
        pdf_note.refresh_creation_date()
        self.result = pdf_note.pdf_name
        return True

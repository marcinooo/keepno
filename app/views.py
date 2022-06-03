"""
Contains common view functions for keepno app.
"""

from flask import Flask, render_template, url_for
from flask_login import current_user
from .notes.models import Note


def page_not_found(_):
    """The view renders 404 error page."""
    url, message = get_return_link_and_message_from_error_page()
    return render_template('errors/404.html', return_url=url, return_message=message), 404


def page_forbidden(_):
    """The view renders 403 error page."""
    url, message = get_return_link_and_message_from_error_page()
    return render_template('errors/403.html', return_url=url, return_message=message), 403


def page_internal_server_error(_):
    """The view renders 500 error page."""
    url, message = get_return_link_and_message_from_error_page()
    return render_template('errors/500.html', return_url=url, return_message=message), 500


def register_error_handlers(app: Flask) -> None:
    """
    Registers all error handlers.
    :param app: keepno instance
    :return: None
    """
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, page_forbidden)
    app.register_error_handler(500, page_internal_server_error)


def get_return_link_and_message_from_error_page() -> tuple[str, str]:
    """
    Returns link and message rendered on error pages.
    :return: tuple of ready url and message
    """
    if current_user.is_authenticated:
        last_edited_note = Note.get_last_edited_note(current_user.id)
        if last_edited_note is None:
            return_url = url_for('notes.add_first_note')
        else:
            return_url = url_for('notes.note', note_id=last_edited_note.id)
        return_message = 'Last edited note'
    else:
        return_url = url_for('accounts.login')
        return_message = 'Login'
    return return_url, return_message

"""
Contains utils for mailing.
"""

from flask_mail import Message
from .app import mail
from typing import List


def send_email(subject: str, sender: str, recipients: List[str], text_body: str, html_body: str) -> None:
    """
    The function sends email.
    :param subject: mail subject
    :param sender: mail sender
    :param recipients: mail recipients
    :param text_body: mail text body
    :param html_body: mail text html
    :return: None
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

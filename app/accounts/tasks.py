"""
Contains task functions for celery worker.
"""

from flask import current_app, render_template

from ..celery import celery
from ..mail import send_email
from .models import User


@celery.task(bind=True)
def send_account_activation_email(_, user_id: int) -> None:
    """
    Sends email with private link to activate account.
    :param user_id: user id
    :return: None
    """
    expire_time = 3 * 24 * 60 * 60  # 3 days
    user = User.find_by_id(user_id)
    token = user.generate_jwt_token(expire_time=expire_time)
    send_email(
        subject='[Keepno] Activate Your Account',
        sender=current_app.config['MAIL_OFFICIAL_SITE_ADDRESS'],
        recipients=[user.email],
        text_body=render_template('mail/activate_account.txt', user=user, token=token),
        html_body=render_template('mail/activate_account.html', user=user, token=token)
    )


@celery.task(bind=True)
def send_reset_password_email(_, user_email: int) -> None:
    """
    Sends email with private link to reset password.
    :param user_email: user email
    :return: None
    """
    expire_time = 1 * 60 * 60  # 1 hour
    user = User.find_by_email(user_email)
    token = user.generate_jwt_token(expire_time=expire_time)
    send_email(
        subject='[Keepno] Reset Your Account Password',
        sender=current_app.config['MAIL_OFFICIAL_SITE_ADDRESS'],
        recipients=[user.email],
        text_body=render_template('mail/reset_password.txt', user=user, token=token),
        html_body=render_template('mail/reset_password.html', user=user, token=token)
    )

"""
Contains view functions for accounts blueprint.
"""

from flask import (Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory)
from flask.wrappers import Response
from flask_login import login_user, logout_user, login_required, current_user

from .models import User, Profile
from .utils import redirect_authenticated_users, active_account_required, save_picture, redirect_to_last_updated_note
from .messages import (
    CONFIRMATION_MAIL_SENT, INVALID_CREDENTIALS, ACCOUNT_CONFIRMED, ACCOUNT_JUST_CONFIRMED, INVALID_CONFIRMATION_LINK,
    NEW_CONFIRMATION_MAIL_SENT, ACCOUNT_UPDATED_SUCCESSFULLY, PASSWORD_CHANGED_SUCCESSFULLY,
    ACCOUNT_DELETED_SUCCESSFULLY, PASSWORD_RESET_SUCCESSFULLY
)
from .forms import (
    RegistrationForm, LoginForm, AccountUpdateForm, ChangePasswordForm, DeleteAccountForm, ResetPasswordEmailInputForm,
    ResetPasswordNewPasswordInputForm
)
from ..notes.models import Note


accounts_blueprint = Blueprint('accounts',  __name__, template_folder='templates')


@accounts_blueprint.route('/register', methods=['GET', 'POST'])
@redirect_authenticated_users
def register() -> str:
    """The view adds new user in keepno app."""
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = User.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save_to_db()
        profile = Profile(user=user)
        profile.generate_gravatar_url()
        profile.save_to_db()
        from .tasks import send_account_activation_email  # pylint: disable=import-outside-toplevel
        send_account_activation_email.delay(user.id)
        login_user(user)
        flash(CONFIRMATION_MAIL_SENT, 'success')
        return redirect(url_for('accounts.unconfirmed'))
    return render_template('accounts/register.html', form=form)


@accounts_blueprint.route('/login', methods=['GET', 'POST'])
@redirect_authenticated_users
def login() -> str:
    """The view logs in user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.is_authenticated and not current_user.active:
                return redirect(url_for('accounts.unconfirmed'))
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect_to_last_updated_note()
        flash(INVALID_CREDENTIALS, 'error')
    return render_template('accounts/login.html', form=form)


@accounts_blueprint.route('/logout')
@login_required
def logout() -> str:
    """The view logs out user."""
    logout_user()
    return render_template('accounts/logout.html')


@accounts_blueprint.route('/unconfirmed')
@login_required
def unconfirmed() -> str:
    """The view notifies user about unconfirmed account."""
    if current_user.active:
        flash(ACCOUNT_CONFIRMED, 'warning')
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('accounts.account')
    return render_template('accounts/unconfirmed.html')


@accounts_blueprint.route('/account')
@login_required
def account() -> str:
    """The view renders user profile page."""
    number_of_notes = Note.count_user_notes(current_user.id)
    return render_template('accounts/account.html', number_of_notes=number_of_notes)


@accounts_blueprint.route('/confirm/<token>')
def activate_account(token: str) -> str:
    """The view activates user account."""
    user = User.verify_jwt_token(token)
    if user:
        user.active = True
        user.save_to_db()
        flash(ACCOUNT_JUST_CONFIRMED, 'success')
        if not current_user.is_authenticated:
            return redirect(url_for('accounts.login'))
        return redirect_to_last_updated_note()
    flash(INVALID_CONFIRMATION_LINK, 'error')
    return redirect(url_for('accounts.unconfirmed'))


@accounts_blueprint.route('/confirm')
@login_required
def resend_confirmation() -> Response:
    """The view sends mail with activation account link."""
    if current_user.active:
        flash(ACCOUNT_CONFIRMED, 'warning')
        return redirect_to_last_updated_note()
    from .tasks import send_account_activation_email  # pylint: disable=import-outside-toplevel
    send_account_activation_email.delay(current_user.id)
    flash(NEW_CONFIRMATION_MAIL_SENT)
    return redirect(url_for('accounts.unconfirmed'))


@accounts_blueprint.route('/media/accounts/img/<filename>')
@login_required
def media_user_img(filename: str) -> Response:
    """The view returns users profile image."""
    image_path = current_app.config['MEDIA_ROOT'] / 'accounts' / 'img'
    return send_from_directory(image_path, filename)


@accounts_blueprint.route('/account/update', methods=['GET', 'POST'])
@login_required
@active_account_required
def account_update() -> str:
    """The view updates user information."""
    form = AccountUpdateForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.change_email(form.email.data)
        current_user.save_to_db()
        current_user.profile.description = form.description.data
        if form.image.data and not form.use_gravatar.data:
            current_user.profile.image = save_picture(form.image.data)
            current_user.profile.custom_image = True
        if form.use_gravatar.data:
            current_user.profile.custom_image = False
        current_user.profile.save_to_db()
        flash(ACCOUNT_UPDATED_SUCCESSFULLY, 'success')
        return redirect(url_for('accounts.account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.description.data = current_user.profile.description
    return render_template('accounts/account_update.html', form=form)


@accounts_blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password() -> str:
    """The view changes current user password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        hashed_password = User.generate_password_hash(form.new_password.data)
        current_user.password = hashed_password
        current_user.save_to_db()
        flash(PASSWORD_CHANGED_SUCCESSFULLY, 'success')
        return redirect(url_for('accounts.account'))
    return render_template('accounts/change_password.html', form=form)


@accounts_blueprint.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account() -> str:
    """The view deletes user account."""
    form = DeleteAccountForm()
    if form.validate_on_submit():
        # add user deletetion
        flash(ACCOUNT_DELETED_SUCCESSFULLY, 'success')
        return redirect(url_for('accounts.login'))
    return render_template('accounts/delete_account.html', form=form)


@accounts_blueprint.route('/reset-password-email-input', methods=['GET', 'POST'])
def reset_password_email_input() -> str:
    """The view sends email with link to reset password page."""
    form = ResetPasswordEmailInputForm()
    if form.validate_on_submit():
        from .tasks import send_reset_password_email  # pylint: disable=import-outside-toplevel
        send_reset_password_email.delay(form.email.data)
        return redirect(url_for('accounts.reset_password_email_sent'))
    return render_template('accounts/reset_password_email_input.html', form=form)


@accounts_blueprint.route('/reset-password-email-sent')
def reset_password_email_sent() -> str:
    """The view shows confirmation of sending email with reset password link."""
    return render_template('accounts/reset_password_email_sent.html')


@accounts_blueprint.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token: str) -> str:
    """The view resets user password."""
    user = User.verify_jwt_token(token)
    if not user:
        flash(INVALID_CONFIRMATION_LINK, 'error')
        return redirect(url_for('accounts.login'))
    form = ResetPasswordNewPasswordInputForm()
    if form.validate_on_submit():
        user.password = User.generate_password_hash(form.password.data)
        user.save_to_db()
        flash(PASSWORD_RESET_SUCCESSFULLY, 'success')
        return redirect(url_for('accounts.login'))
    return render_template('accounts/reset_password_new_password_input.html', form=form)

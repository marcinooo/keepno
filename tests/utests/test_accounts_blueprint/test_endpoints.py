"""
Contains unit tests of endpoints.
"""
import pytest

from app import accounts_models
from app.accounts import tasks



class MockDelay:
    @staticmethod
    def delay():
        pass


class TestRegisterEndpoint:
    """The class tests '/register' endpoint."""

    def test_successful_registration(self, client, monkeypatch):

        def mock_delay(*args, **kwargs):
            return MockDelay()

        monkeypatch.setattr(tasks.send_account_activation_email, "delay", mock_delay)

        resp = client.post('/register', data={
            'username': 'Abraham',
            'email': 'abraham.lincoln@gmail.com',
            'password': 'Abrlin16',
            'confirm_password': 'Abrlin16'
        }, follow_redirects=True)
    
        new_user = accounts_models.User.find_by_username('Abraham')
        assert new_user and not new_user.active
        assert resp.status_code == 200
        html_page =  resp.data.decode('utf-8')
        assert 'alerts.success' in html_page

    def test_registration_with_existing_username_in_db(self, client, user):
        resp = client.post('/register', data={
            'username': 'John',
            'email': 'abraham.lincoln@gmail.com',
            'password': 'Abrlin16',
            'confirm_password': 'Abrlin16'
        })
        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'This username is already taken.' in html_page

    def test_registration_with_existing_email_in_db(self, client, user):
        resp = client.post('/register', data={
            'username': 'Abraham',
            'email': 'john.kennedy@gmail.com',
            'password': 'Abrlin16',
            'confirm_password': 'Abrlin16'
        })
        html_page = resp.data.decode('utf-8')
        assert 'This email is already taken, please select another one.' in html_page

    def test_registration_with_invalid_form_fields(self, client):
        resp = client.post('/register', data={
            'username': 'A',
            'email': 'Invalid mail',
            'password': 'bad',
            'confirm_password': 'bad :(',
        })
        html_page = resp.data.decode('utf-8')

        returned_messages = [
            'Invalid email address.',
            'Field must be between 3 and 50 characters long.',
            'Make sure your password has a number in it.',
            'Field must be equal to password.',
        ]
        assert resp.status_code == 200
        assert all([msg in html_page for msg in returned_messages])


class TestLoginEndpoint:
    """The class tests '/login' endpoint."""
    @pytest.mark.parametrize('email,password,message', [
        ('john.kennedy@gmail.com', 'Ohh', 'Invalid email or password!'),
        ('fake@mail.com', 'Jofken35', 'Invalid email or password!')
    ])
    def test_login_with_invalid_credentials(self, client, user,
                                          email, password, message):
        resp = client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert message in html_page

    def test_login_with_valid_credentials_and_inactive_account(self,
                                                               client, user):
        resp = client.post('/login', data={
            'email': 'john.kennedy@gmail.com',
            'password': 'Jofken35'
        })
        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 302 and 'Redirecting...' in html_page
        assert not user.active

    def test_login_with_valid_credentials_and_active_account(self,
                                                             client, user):
        # Prepare user
        user.active = True
        user.save_to_db()
        # Test endpoint
        resp = client.post('/login', data={
            'email': 'john.kennedy@gmail.com',
            'password': 'Jofken35'
        }, follow_redirects=True)
        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 200 and 'Your first note' in html_page


class TestChangePasswordEndpoint:
    """The class tests '/change-password' endpoint."""

    def test_change_password_request(self, auth_client, user):
        resp = auth_client.post('/change-password', data={
            'old_password': 'Jofken35',
            'new_password': 'Jofken34',
            'confirm_new_password': 'Jofken34',
        }, follow_redirects=True)
        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 200 and 'Your password has been changed successfully.' in html_page

    def test_change_password_with_invalid_new_password_request(self, auth_client, user):
        resp = auth_client.post('/change-password', data={
            'old_password': 'Jofken35',
            'new_password': 'Jofken',
            'confirm_new_password': 'Jofken12',
        }, follow_redirects=True)
        html_page = resp.data.decode('utf-8')
        assert 'Make sure your password has a number in it.' in html_page


class TestActivateAccountEndpoint:
    """The class tests '/confirm/<token>' endpoint."""

    def test_activate_account_with_valid_token_request(self, auth_client, user):
        expire_time = 15  # in seconds
        token = user.generate_jwt_token(expire_time=expire_time)
        resp = auth_client.get(f'/confirm/{token}', follow_redirects=True)
        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 200 and 'You have confirmed your account.' in html_page

    def test_activate_account_with_invalid_token_request(self, auth_client, user):
        token = 'yJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NTQxNzEyOTEuNjY1MjgyNX0.' \
                'gImT1StADPQ-fd0jc0PkYHiQjYbudiK3ODXBFxIzMf4'
        resp = auth_client.get(f'/confirm/{token}', follow_redirects=True)
        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 404


class TestResetPasswordEndpoint:
    """The class tests '/reset-password/<token>' endpoint.""" 

    def test_reset_password_with_valid_token_request(self, client, user):
        expire_time = 15  # in seconds
        token = user.generate_jwt_token(expire_time=expire_time)
        resp = client.post(f'/reset-password/{token}', data={
            'password': 'Jofken99',
            'confirm_password': 'Jofken99'
        }, follow_redirects=True)
        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 200 and 'Your password has been reset.' in html_page

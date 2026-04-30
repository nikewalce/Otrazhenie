from datetime import datetime
from unittest.mock import patch


def test_validate_with_mock(user_service, mock_email_check):
    data = {"username": "user", "email": "a@a.com", "password": "Strong123"}
    validated = user_service.validate_registration_data(data)

    assert validated["email"] == "a@a.com"
    mock_email_check.assert_called_once_with("a@a.com")


@patch("app.services.user_service.OtrazhenieDB.get_user_by_username")
def test_duplicate_username(mocked):
    mocked.return_value = True


@patch("app.services.user_service.OtrazhenieDB")
def test_service_with_fake_db(MockDB):
    MockDB.return_value.get_user_by_email.return_value = None


@patch("requests.get")
def test_api(mock_get):
    mock_get.return_value.status_code = 200

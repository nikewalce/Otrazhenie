from unittest.mock import patch
from datetime import datetime
from random import randint

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

@patch("app.services.demo_service.datetime")
def test_get_current_date(mock_dt, demo_service):
    mock_dt.now.return_value = datetime(2025, 1, 1)
    result = demo_service.get_current_date()
    assert result == datetime(2025, 1, 1)

@patch("app.services.demo_service.random.randint", return_value=7)
def test_generate_random_number(mock_rand, demo_service):
    result = demo_service.generate_random_number()
    assert result == 7

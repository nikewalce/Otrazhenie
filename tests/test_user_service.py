import pytest
from app.exceptions.validation import ValidationError

# Проверка корректного username
def test_valid_username(user_service):
    data = {"username": "validuser", "email": "user@example.com", "password": "StrongPass123"}
    validated = user_service.validate_registration_data(data)
    assert validated["username"] == data["username"]

@pytest.mark.parametrize("username", ["", " ", None])
def test_invalid_username(user_service, username):
    data = {"username": username, "email": "user@example.com", "password": "StrongPass123"}
    with pytest.raises(ValidationError):
        user_service.validate_registration_data(data)

# Проверка email
def test_valid_email(user_service):
    data = {"username": "user1", "email": "user1@example.com", "password": "StrongPass123"}
    validated = user_service.validate_registration_data(data)
    assert validated["email"] == data["email"]

@pytest.mark.parametrize("email", ["invalidemail", "user@", "@example.com", ""])
def test_invalid_email(user_service, email):
    data = {"username": "user1", "email": email, "password": "StrongPass123"}
    with pytest.raises(ValidationError):
        user_service.validate_registration_data(data)

# Проверка силы пароля
@pytest.mark.parametrize(
    "password, expect_error",
    [
        ("StrongPass123", False),
        ("short", True),
        ("12345678", True),
        ("abcdefgh", True),
    ]
)
def test_password_strength(user_service, password, expect_error):
    data = {"username": "user1", "email": "user1@example.com", "password": password}
    if expect_error:
        with pytest.raises(ValidationError):
            user_service.validate_registration_data(data)
    else:
        validated = user_service.validate_registration_data(data)
        assert validated["password"] == password

# Проверка дубликатов username/email
def test_duplicate_email(user_service):
    # Мокаем, что пользователь уже существует
    user_service.db.get_user_by_email = lambda email: True
    data = {"username": "user1", "email": "user1@example.com", "password": "StrongPass123"}
    with pytest.raises(ValidationError):
        user_service.validate_registration_data(data)

def test_duplicate_username(user_service):
    user_service.db.get_user_by_username = lambda username: True
    data = {"username": "user1", "email": "user1@example.com", "password": "StrongPass123"}
    with pytest.raises(ValidationError):
        user_service.validate_registration_data(data)

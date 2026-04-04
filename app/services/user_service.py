from typing import Dict, Optional

from flask_login import UserMixin

from app.db.crud import OtrazhenieDB
from app.db.encrypt import EncryptData
from app.exceptions.validation import ValidationError
from app.schemas.user_schema import UserRegistrationSchema


class User(UserMixin):
    """Объект пользователя для Flask-Login и сервисного слоя"""

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password_hash: str,
        is_active: bool = True,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active

    def check_password(self, password: str) -> bool:
        """Проверяет пароль пользователя"""
        return EncryptData.verify_password(self.password_hash, password)[0]

    def get_id(self):
        """Возвращает ID пользователя как строку (для Flask-Login)"""
        return str(self.id)


class UserService:
    """
    Сервис для работы с пользователями:
    - регистрация
    - аутентификация
    - проверка данных
    """

    def __init__(self, db: Optional[OtrazhenieDB] = None):
        self.db = db or OtrazhenieDB()
        self.schema = UserRegistrationSchema()

    # ---------------- Регистрация ----------------
    def register_user(self, data: Dict) -> User:
        """Создает нового пользователя после валидации"""
        valid_data = self.validate_registration_data(data)

        # Хэшируем пароль
        valid_data["password_hash"] = EncryptData.hash_password(
            valid_data.pop("password")
        )

        # Сохраняем пользователя через CRUD
        user_obj = self.db.create_user(
            username=valid_data["username"],
            email=valid_data["email"],
            password_hash=valid_data["password_hash"],
        )
        return self._to_user_model(user_obj)

    def validate_registration_data(self, data: Dict) -> Dict:
        """Проверяет корректность данных регистрации"""
        errors = self.schema.validate(data)
        if errors:
            raise ValidationError(errors)

        if self.db.get_user_by_email(data["email"]):
            raise ValidationError(
                {"email": "Пользователь с таким email уже существует"}
            )
        if self.db.get_user_by_username(data["username"]):
            raise ValidationError(
                {"username": "Пользователь с таким именем уже существует"}
            )

        self._validate_password_strength(data["password"])
        return self.schema.load(data)

    def _validate_password_strength(self, password: str):
        """Дополнительная проверка сложности пароля"""
        if len(password) < 8:
            raise ValidationError(
                {"password": "Пароль должен быть не менее 8 символов"}
            )
        if password.isdigit():
            raise ValidationError(
                {"password": "Пароль не должен состоять только из цифр"}
            )
        if password.isalpha():
            raise ValidationError(
                {"password": "Пароль должен содержать хотя бы одну цифру"}
            )

    # ---------------- Аутентификация ----------------
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Проверяет email и пароль, возвращает User если верно"""
        user_obj = self.db.get_user_by_email(email)
        if not user_obj:
            return None
        # Проверка пароля
        is_valid, new_hash = EncryptData().verify_password(
            user_obj.password_hash, password
        )
        return self._to_user_model(user_obj) if is_valid else None

    # ---------------- Получение пользователей ----------------
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Возвращает пользователя по ID"""
        user_obj = self.db.get_user_by_id(user_id)
        return self._to_user_model(user_obj) if user_obj else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Возвращает пользователя по email"""
        user_obj = self.db.get_user_by_email(email)
        return self._to_user_model(user_obj) if user_obj else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Возвращает пользователя по username"""
        user_obj = self.db.get_user_by_username(username)
        return self._to_user_model(user_obj) if user_obj else None

    def _to_user_model(self, user_obj) -> User:
        """Конвертирует SQLAlchemy User в сервисный User"""
        return User(
            id=user_obj.id,
            username=user_obj.username,
            email=user_obj.email,
            password_hash=user_obj.password_hash,
            is_active=user_obj.is_active,
        )


# ---------------- Глобальный экземпляр ----------------
user_service = UserService()

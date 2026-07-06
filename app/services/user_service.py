from typing import Dict, Optional
import logging
from flask_login import UserMixin
from pydantic import ValidationError as PydanticValidationError

from app.db.crud import OtrazhenieDB
from app.db.encrypt import EncryptData
from app.exceptions.validation import ValidationError
from app.schemas.user_schema import UserRegistrationSchema

logger = logging.getLogger(__name__)

def mask_email(email: str) -> str:
    """user@example.com -> u***@example.com"""
    try:
        name, domain = email.split("@")
        return f"{name[0]}***@{domain}"
    except Exception:
        return "***@***"

class User(UserMixin):
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password_hash: str,
        is_active: bool = True,
    ):
        logger.debug("Инициализация пользователя: user_id=%s username=%s", id, username)

        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._is_active = is_active

    @property
    def is_active(self) -> bool:
        logger.debug("Проверка is_active для user_id= %s", self.id)
        return self._is_active

    def check_password(self, password: str) -> bool:
        result = EncryptData.verify_password(self.password_hash, password)[0]

        logger.debug(
            "Проверка пароля: user_id=%s result=%s",
            self.id,
            "ok" if result else "fail",
        )

        return result

    def get_id(self):
        return str(self.id)


class UserService:
    db = OtrazhenieDB()

    def register_user(self, data: Dict) -> User:
        logger.info("Попытка регистрации пользователя")

        validated_data = self.validate_registration_data(data)

        logger.debug("Данные регистрации успешно валидированы")

        hash_password = EncryptData().hash_password(validated_data.password)
        logger.debug("Пароль успешно захеширован")

        user_obj = self.db.create_user(
            username=validated_data.username,
            email=validated_data.email,
            password_hash=hash_password,
        )

        logger.info("Пользователь создан в БД: user_id=%s username=%s",
            user_obj.id,
            user_obj.username,
        )

        return self._to_user_model(user_obj)

    def validate_registration_data(self, data: Dict) -> UserRegistrationSchema:
        logger.debug("Валидация данных регистрации: %s", data)

        try:
            validated_user = UserRegistrationSchema(**data)
            logger.debug("Pydantic-валидация прошла успешно")

        except PydanticValidationError as e:
            logger.warning("РЕГИСТРАЦИЯ_ОТКЛОНЕНА причина=ошибка_валидации")
            raise ValidationError(e.errors())

        if self.db.get_user_by_email(validated_user.email):
            logger.warning(
                "РЕГИСТРАЦИЯ_ОТКЛОНЕНА причина=дубликат_email email=%s",
                mask_email(validated_user.email),
            )
            raise ValidationError({"email": "Пользователь с таким email уже существует"})

        if self.db.get_user_by_username(validated_user.username):
            logger.warning(
                "РЕГИСТРАЦИЯ_ОТКЛОНЕНА причина=дубликат_username username=%s",
                validated_user.username,
            )
            raise ValidationError({"username": "Пользователь с таким именем уже существует"})

        logger.debug("РЕГИСТРАЦИЯ_ПРОШЛА_ВАЛИДАЦИЮ_УСПЕШНО")
        return validated_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        logger.info("Попытка аутентификации пользователя")

        user_obj = self.db.get_user_by_email(email)

        if not user_obj:
            logger.warning("ВХОД_НЕУДАЧЕН причина=неверные_данные")
            return None

        is_valid = self.db.verify_user_password(email, password)

        if not is_valid:
            logger.warning(
                "ВХОД_НЕУДАЧЕН причина=неверные_данные user_id=%s",
                user_obj.id
            )
            return None

        logger.info("ВХОД_УСПЕШЕН user_id=%s", user_obj.id)
        return self._to_user_model(user_obj)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        logger.debug("Поиск пользователя по id= %s", user_id)

        user_obj = self.db.get_user_by_id(user_id)

        if not user_obj:
            logger.debug("ПОЛЬЗОВАТЕЛЬ_НЕ_НАЙДЕН user_id=%s", user_id)
            return None

        return self._to_user_model(user_obj)

    def get_user_by_email(self, email: str) -> Optional[User]:
        logger.debug("Поиск пользователя по email: %s", mask_email(email))

        user_obj = self.db.get_user_by_email(email)
        return self._to_user_model(user_obj) if user_obj else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        logger.debug("Поиск пользователя по username= %s", username)

        user_obj = self.db.get_user_by_username(username)
        return self._to_user_model(user_obj) if user_obj else None

    def _to_user_model(self, user_obj) -> User:
        return User(
            id=user_obj.id,
            username=user_obj.username,
            email=user_obj.email,
            password_hash=user_obj.password_hash,
            is_active=user_obj.is_active,
        )


user_service = UserService()
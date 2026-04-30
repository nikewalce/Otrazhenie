import re
from typing import ClassVar, List

from pydantic import BaseModel, EmailStr, field_validator

# ORM модель пользователя (SQLAlchemy)
# Используется ТОЛЬКО для сериализации/десериализации, не для логики
from app.db.models import User


# =========================================================
#         DTO / SCHEMA: регистрация пользователя
# =========================================================
class UserRegistrationSchema(BaseModel):
    """
    Pydantic схема для входных данных регистрации

    Роль класса:
    - проверка входных данных (validation layer)
    - защита сервисного слоя от "грязных" данных
    - единый контракт между UI → service layer

    Важно:
    Это НЕ бизнес-логика.
    Это именно "валидация формы + формата данных".
    """

    # Список обязательных полей (в текущем коде не используется напрямую)
    # можно применять для динамической проверки или генерации UI
    required_fields: ClassVar[List[str]] = ["username", "email", "password"]

    # Username: строка без дополнительных ограничений (валидируется ниже)
    username: str

    # EmailStr — встроенная строгая валидация email от Pydantic
    # Проверяет формат автоматически (regex + RFC правила)
    email: EmailStr

    # Пароль валидируется вручную (через field_validator)
    password: str

    # =========================================================
    #               VALIDATION: username
    # =========================================================
    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        """
        Валидация username

        Проверки:
        1. не пустой
        2. минимальная длина
        3. допустимые символы
        """

        if not username:
            raise ValueError("Username не может быть пустым")

        if len(username) < 3:
            raise ValueError("Username должен содержать от 3 символов")

        # Регулярка:
        # - латиница
        # - цифры
        # - точка
        # - подчёркивание
        if not re.match(r"^[a-zA-Z0-9._]+$", username):
            raise ValueError(
                "Username может содержать символы английского алфавита, числа и нижнее подчеркивания"
            )

        return username

    # =========================================================
    #               VALIDATION: password
    # =========================================================
    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Валидация пароля

        Уровень security validation (очень важно):

        Требования:
        - длина >= 8
        - минимум 1 цифра
        - минимум 1 uppercase
        - минимум 1 lowercase
        - минимум 1 спецсимвол
        """

        if not password:
            raise ValueError("Password не может быть пустым")

        if len(password) < 8:
            raise ValueError("Password должен содержать от 8 символов")

        # Проверка цифры
        if not any(c.isdigit() for c in password):
            raise ValueError("Password должен содержать хотя бы одно число")

        # Проверка заглавной буквы
        if not any(c.isupper() for c in password):
            raise ValueError(
                "Password должен содержать хотя бы один символ верхнего регистра"
            )

        # Проверка строчной буквы
        if not any(c.islower() for c in password):
            raise ValueError(
                "Password должен содержать хотя бы один символ нижнего регистра"
            )

        # Спецсимволы (ограниченный набор)
        special_chars = set("!@#$%^&*")

        if not any(c in special_chars for c in password):
            raise ValueError(
                "Password должен содержать хотя бы один специальный символ !@#$%^&*"
            )

        return password


# =========================================================
#         DTO: публичное представление пользователя
# =========================================================
class UserPublicSchema:
    """
    Схема для отдачи пользователя наружу (API/UI)

    Зачем нужна:
    - скрывает чувствительные поля (например password_hash)
    - контролирует формат ответа
    - защищает от утечек данных

    Это слой "output DTO"
    """

    @staticmethod
    def dump(user: User) -> dict:
        """
        Конвертация ORM/Domain → dict для API/UI

        Важно:
        Мы явно выбираем поля → никакого "auto expose"
        """

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            # ISO формат даты:
            # - стандарт для API
            # - легко парсится фронтом и другими сервисами
            "created_at": (user.created_at.isoformat() if user.created_at else None),
        }

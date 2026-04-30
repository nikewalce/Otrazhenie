from typing import Dict, Optional

# UserMixin — это готовая реализация базовых методов пользователя для Flask-Login:
# - is_authenticated
# - is_active
# - is_anonymous
# - get_id (можно переопределять)
from flask_login import UserMixin

# Ошибка валидации от Pydantic (используется для схем)
from pydantic import ValidationError as PydanticValidationError

# CRUD слой — работает напрямую с БД (SQLAlchemy или другой ORM)
from app.db.crud import OtrazhenieDB

# Класс для работы с паролями:
# - хэширование
# - проверка
from app.db.encrypt import EncryptData

# Кастомная ошибка доменной валидации (твой уровень приложения)
from app.exceptions.validation import ValidationError

# Pydantic-схема для регистрации пользователя
from app.schemas.user_schema import UserRegistrationSchema


class User(UserMixin):
    """
    Доменная модель пользователя (НЕ ORM!)

    Это важный момент:
    - Это НЕ модель БД (не SQLAlchemy)
    - Это объект, с которым работает сервисный слой и Flask-Login

    Зачем это нужно:
    - отделяем БД от бизнес-логики
    - можем менять ORM, не ломая остальной код
    """

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password_hash: str,
        is_active: bool = True,
    ):
        # ID пользователя (используется Flask-Login)
        self.id = id

        # Логин пользователя
        self.username = username

        # Email (используется как основной идентификатор при логине)
        self.email = email

        # Хэш пароля (НИКОГДА не храним пароль в открытом виде)
        self.password_hash = password_hash

        # Флаг активности (можно блокировать пользователя)
        self.is_active = is_active

    def check_password(self, password: str) -> bool:
        """
        Проверяет пароль пользователя

        Как работает:
        1. Берем сохраненный hash
        2. Сравниваем с введенным паролем
        3. verify_password возвращает tuple (bool, ...)
        """
        return EncryptData.verify_password(self.password_hash, password)[0]

    def get_id(self):
        """
        Flask-Login требует, чтобы ID был строкой

        Этот метод используется:
        - при сохранении user_id в сессии
        - при загрузке пользователя (user_loader)
        """
        return str(self.id)


class UserService:
    """
    Сервисный слой (Business Logic Layer)

    Его задача:
    - НЕ работать напрямую с Flask
    - НЕ работать напрямую с ORM
    - управлять логикой приложения

    Здесь происходит:
    - валидация
    - регистрация
    - аутентификация
    """

    # Создаем экземпляр CRUD слоя
    db = OtrazhenieDB()

    # ---------------- Регистрация ----------------
    def register_user(self, data: Dict) -> User:
        """
        Регистрирует пользователя

        Pipeline (очень важно понимать):
        1. Валидация данных (Pydantic + бизнес-правила)
        2. Хэширование пароля
        3. Сохранение в БД
        4. Преобразование в доменную модель
        """

        # 1. Валидируем входные данные
        validated_data = self.validate_registration_data(data)

        # 2. Хэшируем пароль (безопасность)
        hash_password = EncryptData.hash_password(validated_data.password)

        # 3. Сохраняем пользователя в БД через CRUD слой
        user_obj = self.db.create_user(
            username=validated_data.username,
            email=validated_data.email,
            password_hash=hash_password,
        )

        # 4. Конвертируем ORM → доменная модель
        return self._to_user_model(user_obj)

    def validate_registration_data(self, data: Dict) -> UserRegistrationSchema:
        """
        Валидирует данные регистрации

        Уровни валидации:
        1. Pydantic (формат, типы, длины)
        2. Бизнес-логика (уникальность email/username)
        """

        try:
            # Pydantic автоматически:
            # - проверяет типы
            # - проверяет обязательные поля
            # - может делать кастомные валидаторы
            validated_user = UserRegistrationSchema(**data)

        except PydanticValidationError as e:
            # Перехватываем ошибку Pydantic и преобразуем в свою
            # Это важно, чтобы:
            # - не "протекали" внешние зависимости наружу
            # - унифицировать ошибки
            print(f"Ошибка валидации: {e}")

            raise ValidationError(e.errors())

        # Проверка уникальности email
        if self.db.get_user_by_email(validated_user.email):
            raise ValidationError(
                {"email": "Пользователь с таким email уже существует"}
            )

        # Проверка уникальности username
        if self.db.get_user_by_username(validated_user.username):
            raise ValidationError(
                {"username": "Пользователь с таким именем уже существует"}
            )

        return validated_user

    # ---------------- Аутентификация ----------------
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Аутентификация пользователя (логин)

        Логика:
        1. Ищем пользователя по email
        2. Если нет — возвращаем None
        3. Проверяем пароль
        4. Если верно — возвращаем User
        """

        # Получаем пользователя из БД
        user_obj = self.db.get_user_by_email(email)

        # Если пользователь не найден
        if not user_obj:
            return None

        # Проверяем пароль через CRUD слой
        # (возможно внутри используется EncryptData)
        is_valid = self.db.verify_user_password(email, password)

        # Если пароль верный → возвращаем доменную модель
        return self._to_user_model(user_obj) if is_valid else None

    # ---------------- Получение пользователей ----------------
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID

        Используется:
        - Flask-Login (user_loader)
        """
        user_obj = self.db.get_user_by_id(user_id)
        return self._to_user_model(user_obj) if user_obj else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        user_obj = self.db.get_user_by_email(email)
        return self._to_user_model(user_obj) if user_obj else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        user_obj = self.db.get_user_by_username(username)
        return self._to_user_model(user_obj) if user_obj else None

    def _to_user_model(self, user_obj) -> User:
        """
        Конвертер ORM → доменная модель

        Зачем:
        - не тащим SQLAlchemy объекты в бизнес-логику
        - контролируем, какие поля доступны
        - изолируем слой БД

        Это ключевой элемент "чистой архитектуры"
        """
        return User(
            id=user_obj.id,
            username=user_obj.username,
            email=user_obj.email,
            password_hash=user_obj.password_hash,
            is_active=user_obj.is_active,
        )


# ---------------- Глобальный экземпляр ----------------
# Упрощение:
# можно импортировать user_service в любом месте приложения

user_service = UserService()

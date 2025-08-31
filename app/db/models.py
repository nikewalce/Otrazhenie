from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Table, Text
from app.db.session import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class ProductIngredient(Base):
    """Класс для таблицы с ингредиентами"""

    __tablename__ = "product_ingredients"

    id = Column(Integer, primary_key=True, index=True)  # уникальный ID
    name = Column(String, nullable=False, unique=True)  # название ингредиента
    safety_score = Column(Float, nullable=True)  # рейтинг безопасности
    description = Column(String, nullable=True)  # описание
    # внешний ключ на категорию (назначение/функцию)
    category_id = Column(Integer, ForeignKey("ingredient_categories.id"), nullable=True)
    category = relationship("IngredientCategory", back_populates="ingredients")

    def __repr__(self):
        return (
            f"ProductIngredient(\nid={self.id}, \nname='{self.name}', "
            f"\ncategory_id='{self.category_id}', \nsafety_score={self.safety_score}, "
            f"\ndescription='{self.description}')"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "safety_score": self.safety_score,
            "description": self.description
        }

class IngredientCategory(Base):
    """Класс для категорий ингредиентов"""
    __tablename__ = "ingredient_categories"

    id = Column(Integer, primary_key=True, index=True)  # уникальный ID
    name_en = Column(String, nullable=False, unique=True)  # название на английском
    name_ru = Column(String, nullable=True)  # перевод на русский
    description = Column(String, nullable=True)  # пояснение/описание
    # Связь один ко многим: категория → ингредиенты
    ingredients = relationship("ProductIngredient", back_populates="category")

    def __repr__(self):
        return (f"IngredientCategory(\nid={self.id}, \nname_en='{self.name_en}', "
                f"\nname_ru='{self.name_ru}'), \ndescription='{self.description}')")

    def to_dict(self):
        return {
            "id": self.id,
            "name_en": self.name_en,
            "name_ru": self.name_ru,
            "description": self.description
        }

# Таблица связей между ролями и правами
role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Таблица связей между пользователями и ролями (многие-ко-многим)
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class User(Base):
    """Класс пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # Уникальный ID пользователя
    username = Column(String(50), unique=True, nullable=False)  # Логин / ник
    email = Column(String(120), unique=True, nullable=False)  # Электронная почта
    password_hash = Column(String(256), nullable=False)  # Хэш пароля
    created_at = Column(DateTime, default=datetime.now(timezone.utc))  # Дата регистрации
    last_login = Column(DateTime, default=None, onupdate=datetime.now(timezone.utc))  # Дата последнего входа
    is_active = Column(Boolean, default=True)  # Активен или нет

    profile = relationship("Profile", uselist=False, back_populates="user")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("Session", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    messages = relationship("Message", back_populates="user")
    activities = relationship("ActivityLog", back_populates="user")
    reset_tokens = relationship("PasswordResetToken", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class Profile(Base):
    """Профиль пользователя"""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    avatar_url = Column(String(256))
    bio = Column(Text)

    user = relationship("User", back_populates="profile")


class Role(Base):
    """Роль пользователя"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Права доступа"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Session(Base):
    """Сессии пользователя"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(256), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="sessions")


class Notification(Base):
    """Уведомления"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")


class Message(Base):
    """Сообщения"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_sent = Column(Boolean, default=True)

    user = relationship("User", back_populates="messages")


class ActivityLog(Base):
    """История активности пользователя"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="activities")


class PasswordResetToken(Base):
    """Токены восстановления пароля"""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)

    user = relationship("User", back_populates="reset_tokens")
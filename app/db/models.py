from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from app.db.session import Base
from sqlalchemy.orm import relationship
from datetime import datetime


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

class User(Base):
    """Класс пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User {self.username}>"
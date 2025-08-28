# описания таблиц (SQLAlchemy ORM)

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.session import Base
from sqlalchemy.orm import relationship

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
            f"\nfunction='{self.function}', \nsafety_score={self.safety_score}, "
            f"\ndescription='{self.description}')"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "function": self.category.to_dict() if self.category else None,
            "safety_score": self.safety_score,
            "description": self.description
        }

class IngredientCategory(Base):
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

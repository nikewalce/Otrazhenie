from unicodedata import category

from app.db.session import Database, Base
from app.db.models import ProductIngredient, IngredientCategory

class OtrazhenieDB(Database):
    """Класс для работы с таблицами"""

    def create_tables(self):
        """Создаёт все таблицы, которые определены в моделях"""
        Base.metadata.create_all(self.engine)
        print("Таблицы созданы!")

    def delete_tables(self):
        """Удаляет все таблицы, которые определены в моделях"""
        Base.metadata.drop_all(self.engine)
        print("Таблицы удалены!")

    def add_ingredient(self, name: str, category_id: int = None, safety_score: float = None, description: str = None):
        """Добавляет новый ингредиент"""
        with self.get_session() as session:
            ingredient = ProductIngredient(
                name=name,
                category_id=category_id,
                safety_score=safety_score,
                description=description
            )
            session.add(ingredient)
            session.commit() # фиксируем изменения
            session.refresh(ingredient)
            return ingredient

    def add_category(self, name_en: str = None, name_ru: str = None, description: str = None):
        """Добавляет новую категорию ингредиентов"""
        with self.get_session() as session:
            category = IngredientCategory(
                name_en=name_en,
                name_ru=name_ru,
                description=description
            )
            session.add(category)
            session.commit()
            session.refresh(category)  # обновляем, чтобы получить ID
            return category

    def update_ingredient(self, ingredient_id: int, name: str = None, function: str = None,
                          safety_score: float = None, description: str = None):
        """Обновляет данные ингредиента"""
        with self.get_session() as session:
            ingredient = session.query(ProductIngredient).filter(ProductIngredient.id == ingredient_id).first()
            if not ingredient:
                return None
            if name:
                ingredient.name = name
            if function:
                ingredient.function = function
            if safety_score is not None:
                ingredient.safety_score = safety_score
            if description:
                ingredient.description = description
            session.commit() # фиксируем изменения
            session.refresh(ingredient) # обновляем объект после commit
            return ingredient


    def delete_ingredient(self, ingredient_id: int):
        """Удаляет ингредиент по ID"""
        with self.get_session() as session:
            ingredient = session.query(ProductIngredient).filter(ProductIngredient.id == ingredient_id).first()
            if not ingredient:
                return None
            session.delete(ingredient)
            session.commit() # фиксируем изменения
            return ingredient

    def select_all_categories(self):
        """Возвращает все категории из таблицы ingredient_categories"""
        with self.get_session() as session:
            return session.query(IngredientCategory).all()

    def select_all_ingredients(self):
        """Возвращает все записи из таблицы product_ingredients"""
        with self.get_session() as session:
            return session.query(ProductIngredient).all()

    def select_one_ingredient(self, ingredient_name: str):
        """
        Возвращает один ингредиент
        :param ingredient_name: имя ингредиента
        """
        with self.get_session() as session:
            return session.query(ProductIngredient).filter(ProductIngredient.name == ingredient_name).first()  # одна запись

#print(add_ingredient("aqua", "solvent",5,"Вода — основной растворитель в косметике"))
# ingredients = OtrazhenieDB().select_all_ingredients()
ingredients = OtrazhenieDB().select_all_categories()
for ing in ingredients:
    print(ing.to_dict())


# print(OtrazhenieDB().select_one_ingredient("aqua"))

# OtrazhenieDB().create_tables()
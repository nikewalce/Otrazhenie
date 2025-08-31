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
        """Добавляет новый ингредиент
        :param name: название ингредиента
        :param category_id: id категории из таблицы ingredient_categories
        :param safety_score: оценка безопасности ингредиента (1 - безопасен, 10 - вреден)
        :param description: Описание ингредиента
        """
        with self.get_session() as session:
            ingredient = ProductIngredient(
                name=name,
                safety_score=safety_score,
                description=description,
                category_id=category_id
            )
            session.add(ingredient)
            session.commit() # фиксируем изменения
            session.refresh(ingredient)
            return ingredient

    def add_category(self, name_en: str = None, name_ru: str = None, description: str = None):
        """Добавляет новую категорию ингредиентов
        :param name_en: наименование категории на английском
        :param name_ru: наименование категории на русском
        :param description: описание категории
        """
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

    def select_all_ingredients_with_names(self):
        """Возвращает все записи из таблицы product_ingredients с названиями ингредиентов вместо внешних ключей"""
        with self.get_session() as session:
            # Выполняем JOIN запрос между таблицами product_ingredients и ingredients
            results = session.query(
                ProductIngredient.id,
                ProductIngredient.name,
                IngredientCategory.name_ru.label('ingredient_name'),  # Берем русское название ингредиента
                ProductIngredient.safety_score,
                ProductIngredient.description
            ).join(
                IngredientCategory,  # Указываем таблицу для JOIN
                ProductIngredient.category_id == IngredientCategory.id  # Условие соединения
            ).all()
            return results

    def select_one_ingredient(self, ingredient_name: str):
        """
        Возвращает один ингредиент
        :param ingredient_name: имя ингредиента
        """
        with self.get_session() as session:
            return session.query(ProductIngredient).filter(ProductIngredient.name == ingredient_name).first()  # одна запись

if __name__ == '__main__':
    db = OtrazhenieDB()
    # db.delete_tables()
    #db.create_tables()
    # db.select_one_ingredient("aqua")
    ingredients = OtrazhenieDB().select_all_ingredients()
    print('Вывод ингредиентов')
    for ing in ingredients:
        print(ing.to_dict())
    categories = OtrazhenieDB().select_all_categories()
    print('Вывод категорий ингедиентов')
    for category in categories:
        print(category.to_dict())

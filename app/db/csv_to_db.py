from app.db.session import Database, Base
from app.db.models import ProductIngredient, IngredientCategory
import csv

class CSVToDB(Database):
    def import_categories_from_csv(self, file_path: str):
        """
        Импорт категорий (ingredient_categories) из CSV
        Ожидаемые поля: name_en, name_ru, description
        """
        with self.get_session() as session:
            with open(file_path, newline='', encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # проверяем наличие по уникальному name_en
                    existing = session.query(IngredientCategory).filter_by(name_en=row["name_en"]).first()
                    if existing:
                        continue
                    category = IngredientCategory(
                        name_en=row["name_en"],
                        name_ru=row.get("name_ru"),
                        description=row.get("description")
                    )
                    session.add(category)
                session.commit()
        print("Категории импортированы!")

    def import_ingredients_from_csv(self, file_path: str):
        """
        Импорт ингредиентов (product_ingredients) из CSV
        Ожидаемые поля: name, function_id, safety_score, description
        """
        with self.get_session() as session:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing = session.query(ProductIngredient).filter_by(name=row["name"]).first()
                    if existing:
                        continue

                    # Получаем category_id из CSV и преобразуем в int
                    category_id = None
                    if row.get("category_id"):
                        try:
                            category_id = int(row["category_id"])
                        except (ValueError, TypeError):
                            category_id = None

                    ingredient = ProductIngredient(
                        name=row["name"],
                        safety_score=int(row["safety_score"]) if row.get("safety_score") else None,
                        description=row.get("description"),
                        category_id=category_id
                    )
                    session.add(ingredient)
                session.commit()
        print("Ингредиенты импортированы!")

#CSVToDB().import_categories_from_csv("csv_files/ingredient_categories.csv")
CSVToDB().import_ingredients_from_csv("csv_files/ingredients.csv")
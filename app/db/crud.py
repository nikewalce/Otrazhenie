from app.db.session import Database, Base
from app.db.models import ProductIngredient, IngredientCategory, User, Product
from app.db.encrypt import EncryptData

class OtrazhenieDB(Database):
    """Класс для работы с таблицами"""

    def create_tables(self):
        """Создаёт все таблицы, которые определены в моделях"""
        Base.metadata.create_all(self.engine)
        print("Таблицы созданы!")

    def create_table(self, table_class):
        """
        Создаёт конкретную таблицу в базе.

        :param engine: SQLAlchemy engine
        :param table_class: ORM класс таблицы, например Product
        """
        # Определяем объект таблицы
        if hasattr(table_class, "__table__"):  # ORM-класс
            table = table_class.__table__
        else:  # объект Table
            table = table_class
        inspector = self.inspect

        # Проверяем, есть ли уже таблица в базе
        if table.name not in inspector.get_table_names():
            table.create(self.engine)
            print(f"Таблица '{table.name}' создана!")
        else:
            print(f"Таблица '{table.name}' уже существует.")

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

    def add_product(
            self,
            barcode: int,
            name: str,
            brand: str = None,
            ingredients_text: str = None,
            ingredients_text_ru: str = None,
            image_url: str = None,
            packaging: str = None,
            quantity: int = None,
            countries: str = None
    ):
        """
        Добавляет новый продукт в базу.

        :param barcode: штрихкод продукта
        :param name: название продукта
        :param brand: бренд
        :param ingredients_text: список ингредиентов, строка (англ)
        :param ingredients_text_ru: список ингредиентов, строка (рус)
        :param image_url: ссылка на изображение
        :param packaging: упаковка
        :param quantity: количество
        :param countries: страна производства
        :return: объект Product
        """
        with self.get_session() as session:
            # Проверяем, есть ли уже продукт с таким barcode
            existing_product = session.query(Product).filter_by(barcode=barcode).first()
            if existing_product:
                return existing_product  # можно обновить данные, если нужно

            # Создаём продукт
            product = Product(
                barcode=barcode,
                name=name,
                brand=brand,
                ingredients_text=ingredients_text,
                ingredients_text_ru=ingredients_text_ru,
                image_url=image_url,
                packaging=packaging,
                quantity=quantity,
                countries=countries
            )
            ingredients_list = [item.strip() for item in ingredients_text.split(',')]
            # Добавляем ингредиенты
            if ingredients_list:
                for ing_name in ingredients_list:
                    # Ищем ингредиент в базе, если нет — создаём
                    ingredient = session.query(ProductIngredient).filter_by(name=ing_name).first()
                    if not ingredient:
                        ingredient = ProductIngredient(name=ing_name)
                        session.add(ingredient)
                        session.flush()  # чтобы получить id
                    product.ingredients.append(ingredient)

            # Добавляем продукт в сессию и сохраняем
            session.add(product)
            session.commit()
            session.refresh(product)
            return product

    def add_ingredient_with_category(self, name: str, category_name_ru: str = None, category_name_en: str = None,
                       description_category: str = None, safety_score: float = None, description: str = None):
        """Добавляет новый ингредиент с проверкой категории.
        Если категории нет — создается новая.

        :param name: название ингредиента
        :param category_name_ru: название категории на русском
        :param category_name_en: название категории на английском
        :param description_category: описание для категории
        :param safety_score: оценка безопасности (1 - безопасен, 10 - вреден)
        :param description: описание ингредиента
        """
        with self.get_session() as session:
            category_id = None

            # Проверяем, передано ли имя категории
            if category_name_ru or category_name_en:
                query = session.query(IngredientCategory)
                if category_name_ru:
                    query = query.filter(IngredientCategory.name_ru == category_name_ru)
                elif category_name_en:
                    query = query.filter(IngredientCategory.name_en == category_name_en)

                category = query.first()

                if category:
                    category_id = category.id
                else:
                    category = self.add_category(
                        name_ru = category_name_ru,
                        name_en = category_name_en,
                        description = description_category
                    )
                    category_id = category.id

            # Создаем ингредиент
            ingredient = self.add_ingredient(
                name=name,
                safety_score=safety_score,
                description=description,
                category_id=category_id
            )
            return ingredient

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

    # --- Функции для пользователей ---
    def create_user_table(self):
        """Создаёт только таблицу пользователей"""
        User.__table__.create(self.engine, checkfirst=True)
        print("Таблица users создана!")

    def delete_user_table(self):
        """Удаляет только таблицу пользователей"""
        User.__table__.drop(self.engine, checkfirst=True)
        print("Таблица users удалена!")

    def select_all_users(self):
        """Возвращает всех юзеров"""
        with self.get_session() as session:
            return session.query(User).all()

    def get_user_by_email(self, email: str):
        """Возвращает пользователя по email"""
        with self.get_session() as session:
            return session.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str):
        """Возвращает пользователя по username"""
        with self.get_session() as session:
            return session.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int):
        """Возвращает пользователя по ID"""
        with self.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()

    def create_user(self, username: str, email: str, password: str):
        """Создаёт нового пользователя"""
        encryptor = EncryptData()
        with self.get_session() as session:
            user = User(
                username=username,
                email=email,
                password_hash=encryptor.hash_password(password)
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def verify_user_password(self, email: str, password: str):
        """Проверяет пароль пользователя"""
        encryptor = EncryptData()
        with self.get_session() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return False

            is_valid, new_hash = encryptor.verify_password(user.password_hash, password)
            if is_valid and new_hash:
                # обновляем хеш в базе на Argon2
                user.password_hash = new_hash
                session.commit()
            return is_valid

if __name__ == '__main__':
    db = OtrazhenieDB()
    # db.delete_tables()
    #db.create_tables()
    # db.select_one_ingredient("aqua")
    # ingredients = OtrazhenieDB().select_all_ingredients()
    # print('Вывод ингредиентов')
    # for ing in ingredients:
    #     print(ing.to_dict())
    # categories = OtrazhenieDB().select_all_categories()
    # print('Вывод категорий ингедиентов')
    # for category in categories:
    #     print(category.to_dict())
    # db.create_user_table()
    users = db.select_all_users()
    for user in users:
        print(user.to_dict())
    # db.create_table(Product)
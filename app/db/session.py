# подключение/engine/Session
from decouple import config
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base,  Session

load_dotenv()

DATABASE_URL = config("DATABASE_URL")
Base = declarative_base() # Базовый класс для определения моделей (таблиц ORM)

class Database:
    """Класс для работы с PostgreSQL через SQLAlchemy"""

    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(db_url, future=True) # создаём подключение к базе данных
        # Создаём фабрику сессий
        self.SessionLocal = sessionmaker(
            bind=self.engine,  # подключение к конкретной базе
            autoflush=False,  # автоматическая очистка изменений перед запросами
            autocommit=False,  # управление транзакциями вручную
            class_=Session  # используем ORM сессию
        )
        self.inspect = inspect(self.engine)

    def get_session(self):
        """Метод для получения сессии через контекстный менеджер
        Пример использования:
            with db.get_session() as session:
                # работа с базой
        """
        return self.SessionLocal()  # Возвращает объект сессии, который закрывается после выхода из блока with

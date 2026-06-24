# подключение/engine/Session
from decouple import config
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, declarative_base, sessionmaker
import logging
load_dotenv()
logger = logging.getLogger(__name__)

# Используем значение по умолчанию для DATABASE_URL если переменная окружения не установлена
try:
    DATABASE_URL = config("DATABASE_URL")
except Exception:
    logger.exception("Используется значение по умолчанию для DATABASE_URL, переменная окружения не установлена")
    DATABASE_URL = "sqlite:///./test.db"  # Используем SQLite для тестирования

Base = declarative_base()  # Базовый класс для определения моделей (таблиц ORM)


class Database:
    """Класс для работы с PostgreSQL через SQLAlchemy"""

    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(
            db_url, future=True
        )  # создаём подключение к базе данных
        logger.info("Подключение к БД создано!")
        # Создаём фабрику сессий
        self.SessionLocal = sessionmaker(
            bind=self.engine,  # подключение к конкретной базе
            autoflush=False,  # автоматическая очистка изменений перед запросами
            autocommit=False,  # управление транзакциями вручную
            class_=Session,  # используем ORM сессию
        )
        logger.info("Фабрика сессий создана!")
        self.inspect = inspect(self.engine)

    def get_session(self):
        """Метод для получения сессии через контекстный менеджер
        Пример использования:
            with db.get_session() as session:
                # работа с базой
        """
        logger.info("Получен объект сессии: %s", self.SessionLocal())
        return (
            self.SessionLocal()
        )  # Возвращает объект сессии, который закрывается после выхода из блока with

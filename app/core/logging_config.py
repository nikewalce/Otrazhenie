import logging
from decouple import config
from dotenv import load_dotenv

load_dotenv()

def setup_logging() -> None:
    """Централизованный конфиг логирования для Flask app.
    Здесь должны жить:
    формат строк логов;
    уровень по умолчанию;
    чтение LOG_LEVEL из окружения;
    Уровни:
    DEBUG — технические детали для разработки (payload, промежуточные данные).
    INFO — бизнес-события и штатные шаги (нашёл штрихкод, продукт не найден, шаг завершён).
    WARNING — ситуация не критична, но что-то пошло не идеально (нет optional dependency, не прочитан кадр).
    ERROR — ошибка операции, но процесс/приложение продолжает жить.
    CRITICAL — только для действительно аварийных случаев
    """

    level_name = config("LOG_LEVEL", default="INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    if logging.getLogger().handlers:
        logging.getLogger().setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

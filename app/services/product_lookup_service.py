from time import sleep
from typing import Callable
import logging
from cachetools import TTLCache

from app.analyzers.qr_reader import get_cosmetic_info
from app.schemas.product_dto import ProductDTO

logger = logging.getLogger(__name__)

# - нормализацией ответа OpenBeautyFacts в внутренний DTO
# изоляция внешних зависимостей + управление надежностью Route → Service → (Cache → Retry → API) → DTO → Route
cache = TTLCache(
    maxsize=1000, ttl=300
)  # maxsize - текущий размер кэша, ttl - Значение времени жизни элементов в кэше (5 минут)


def fetch_with_retry(
    api_function: Callable[[str], ProductDTO | None], barcode: str, retries: int = 3
) -> ProductDTO | None:
    # Экспоненциальное откладывание (exponential backoff),
    # пробуем 3 раза обращаться к API, если не работает -> None
    for attempt in range(retries):
        try:
            logger.debug(
                "Попытка запроса к API: barcode=%s, попытка %s из %s",
                barcode,
                attempt + 1,
                retries
            )
            result = api_function(barcode)

            if result:
                logger.info(
                    "УСПЕХ: товар найден в API: barcode=%s, попытка %s",
                    barcode,
                    attempt + 1
                )
                return result
            else:
                logger.debug(
                    "API вернул пустой результат: barcode=%s, попытка %s из %s",
                    barcode,
                    attempt + 1,
                    retries
                )
        except Exception as e:
            logger.exception(
                "ОШИБКА API: barcode=%s, попытка %s из %s",
                barcode,
                attempt + 1,
                retries
            )
        sleep(2**attempt)  # backoff
        logger.warning(
            "ИТОГ: товар НЕ НАЙДЕН после всех попыток: barcode=%s, попыток=%s",
            barcode,
            retries
        )
    return None


def get_product_info_from_api(barcode: str):
    """Получение данных о продукте из API В продакшене можно поменять на Redis"""
    # 1. cache
    if barcode in cache:
        logger.info("CACHE HIT: код=%s (данные взяты из кеша)", barcode)
        return cache[barcode]
    logger.info("CACHE MISS: код=%s (обращение к API)", barcode)
    # 2. API + retry
    data = fetch_with_retry(get_cosmetic_info, barcode, 3)
    # 3. cache only valid data
    if data:
        logger.info("ИТОГ: продукт НАЙДЕН (barcode=%s)", barcode)
        cache[barcode] = data
    else:
        logger.warning("ИТОГ: продукт НЕ НАЙДЕН (barcode=%s)", barcode)
    return data

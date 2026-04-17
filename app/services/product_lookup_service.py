from app.analyzers.qr_reader import get_cosmetic_info
from app.schemas.product_dto import ProductDTO
from time import sleep
from typing import Callable
from cachetools import TTLCache

# - нормализацией ответа OpenBeautyFacts в внутренний DTO
# изоляция внешних зависимостей + управление надежностью Route → Service → (Cache → Retry → API) → DTO → Route
cache = TTLCache(maxsize=1000, ttl=300)  # maxsize - текущий размер кэша, ttl - Значение времени жизни элементов в кэше (5 минут)

def fetch_with_retry(
    api_function: Callable[[str], ProductDTO | None],
    barcode: str,
    retries: int = 3
) -> ProductDTO | None:
    # Экспоненциальное откладывание (exponential backoff),
    # пробуем 3 раза обращаться к API, если не работает -> None
    for attempt in range(retries):
        try:
            result = api_function(barcode)

            if result:
                return result
        except Exception as e:
            print(f"Ошибка API: {e}")
        sleep(2 ** attempt)  # backoff
    return None


def get_product_info_from_api(barcode: str):
    """ Получение данных о продукте из API В продакшене можно поменять на Redis """
    # 1. cache
    if barcode in cache:
        return cache[barcode]
    # 2. API + retry
    data = fetch_with_retry(get_cosmetic_info, barcode, 3)
    # 3. cache only valid data
    if data:
        cache[barcode] = data
    return data

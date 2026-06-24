import requests
from PIL import Image
import logging
import importlib
from app.schemas.product_dto import ProductDTO
from app.schemas.products_schema import OpenBeautyFactsResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# =========================================================
#                   UTILS
# =========================================================
def _load_optional_dependency(module_name: str):
    """Безопасная загрузка optional зависимостей"""
    try:
        logger.debug("Попытка загрузки зависимости: %s", module_name)
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        logger.warning(
            "optional_dependency_missing: %s", module_name,
        )
        return None


def parse_api_response(data: dict) -> OpenBeautyFactsResponse | None:
    try:
        logger.debug("Парсинг ответа API")
        return OpenBeautyFactsResponse.model_validate(data)
    except ValidationError:
        logger.exception("Ошибка валидации ответа OpenBeautyFacts")
        return None


def read_barcode_from_image(image_path):
    # lazy imports для усиления устойчивости
    try:
        logger.info("Чтение штрих-кода из изображения: %s", image_path)
        from pyzbar import pyzbar
    except ImportError:
        logger.exception("pyzbar/zbar не установлен, чтение штрих-кода недоступно")
        return

    try:
        image = Image.open(image_path)
        logger.debug("Изображение успешно открыто")
    except Exception:
        logger.exception("Ошибка открытия изображения: %s", image_path)
        return

    barcodes = pyzbar.decode(image)
    logger.info("Найдено штрих-кодов: %s", len(barcodes))

    if not barcodes:
        logger.warning("Штрих-коды не найдены на изображении")

    for barcode in barcodes:
        # extra - специальный параметр, который позволяет передать дополнительные контекстные данные
        # в лог-сообщение, сохраняя данные в виде структурированного словаря отдельно от основного текста сообщения
        code = barcode.data.decode("utf-8")
        logger.info("Штрих-код: %s", code)
        product_info = get_cosmetic_info(code)
        logger.info("Информация о товаре: %s", product_info)


def scan_barcode():
    # lazy imports для усиления устойчивости
    try:
        logger.info("Запуск камеры для сканирования штрих-кодов")
        import cv2
        from pyzbar import pyzbar
    except ImportError:
        logger.exception("OpenCV или pyzbar не установлены, сканирование с камеры недоступно")
        return

    cap = cv2.VideoCapture(0)  # Используем камеру

    if not cap.isOpened():
        logger.error("Не удалось открыть камеру")
        return

    logger.info("Камера успешно запущена")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Не удалось получить кадр с камеры")
            break

        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            logger.info("Обнаружен штрих-код: %s (%s)", barcode_data, barcode_type)

            # Рисуем рамку вокруг штрих-кода
            x, y, w, h = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Выводим данные штрих-кода
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(
                frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

            # Получаем информацию о косметике
            product_info = get_cosmetic_info(barcode_data)
            logger.info("Информация о товаре: %s", product_info)

        cv2.imshow("Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            logger.info("Выход из сканирования по нажатию Q")
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("Камера закрыта")


def get_cosmetic_info(barcode: str) -> ProductDTO | None:
    """Получает информацию о продукте по штрих-коду"""
    try:
        logger.info("Запрос API OpenBeautyFacts: %s", barcode)

        response = requests.get(
            f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json",
            timeout=5,  # если API не ответил за 5 секунд — считаем, что он умер
        )

        logger.debug("Ответ API получен: %s", response.status_code)

        try:
            data = parse_api_response(response.json())
        except Exception:
            logger.exception(
                "Ошбика JSON парсинга OpenBeautyFacts: barcode=%s status=%s",
                barcode,
                response.status_code,
            )
            return None

        if not data:
            logger.warning("После анализа ответа API остается пустым: barcode=%s", barcode)
            return None

        if data.status == 1:
            product = data.product
            validate_product = {
                "barcode": barcode,
                "name": product.product_name or "Неизвестно",
                "brand": product.brands or "",
                "category": product.categories or "",
                "ingredients": product.ingredients_text_en or "",
                "image_url": product.image_front_url,
                "additional_info": {
                    "Упаковка": product.packaging or "",
                    "Вес": product.quantity or "",
                    "Страна": product.countries or "",
                },
            }

            logger.info("Продукт успешно получен: %s", barcode)
            return ProductDTO.model_validate(validate_product)

        logger.warning("Продукт не найден: %s", barcode)
        return None

    except requests.Timeout:
        logger.warning("Таймаут OpenBeautyFacts: штрих-код=%s", barcode)

    except requests.RequestException:
        logger.exception("Ошибка запроса OpenBeautyFacts: штрих-код=%s", barcode)

    except Exception:
        logger.exception("Неожиданная ошибка OpenBeautyFacts: штрих-код=%s", barcode)

if __name__ == "__main__":
    barcode = read_barcode_from_image("img_example/barcode.jpg")
    print(get_cosmetic_info(barcode))
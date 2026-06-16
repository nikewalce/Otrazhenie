import requests
from PIL import Image
import logging
import importlib
from app.schemas.product_dto import ProductDTO
from app.schemas.products_schema import OpenBeautyFactsResponse

logger = logging.getLogger(__name__)

# =========================================================
#                   UTILS
# =========================================================
def _load_optional_dependency(module_name: str):
    """Безопасная загрузка optional зависимостей"""
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        logger.warning(
            "optional_dependency_missing",
            extra={"module": module_name},
        )
        return None

def parse_api_response(data: dict) -> OpenBeautyFactsResponse | None:
    try:
        return OpenBeautyFactsResponse.model_validate(data)
    except Exception:
        logger.exception("Ошибка валидации API")
        return None


def read_barcode_from_image(image_path):
    # lazy imports для усиления устойчивости
    try:
        from pyzbar import pyzbar
    except ImportError:
        logger.exception("pyzbar/zbar не установлен, чтение штрих-кода недоступно")
        return
    image = Image.open(image_path)
    barcodes = pyzbar.decode(image)

    for barcode in barcodes:
        # extra - специальный параметр, который позволяет передать дополнительные контекстные данные
        # в лог-сообщение, сохраняя данные в виде структурированного словаря отдельно от основного текста сообщения
        logger.info("Штрих-код:", extra={"barcode": barcode.data.decode("utf-8")})
        product_info = get_cosmetic_info(barcode.data.decode("utf-8"))
        logger.info("Информация о товаре:", extra={"product_info": product_info})


def scan_barcode():
    # lazy imports для усиления устойчивости
    try:
        import cv2
        from pyzbar import pyzbar
    except ImportError:
        logger.exception("OpenCV или pyzbar не установлены, сканирование с камеры недоступно")
        return
    cap = cv2.VideoCapture(0)  # Используем камеру

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

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
            logger.info("Информация о товаре:", extra={"product_info": product_info})

        cv2.imshow("Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def get_cosmetic_info(barcode: str) -> ProductDTO | None:
    """Получает информацию о продукте по штрих-коду"""
    try:
        response = requests.get(
            f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json",
            timeout=5,  # если API не ответил за 5 секунд — считаем, что он умер
        )
        data = parse_api_response(response.json())
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
            return ProductDTO.model_validate(validate_product)
        return None
    except Exception as e:
        logger.exception("Ошибка API")
        return None


if __name__ == "__main__":
    barcode = read_barcode_from_image("img_example/barcode.jpg")
    print(get_cosmetic_info(barcode))

# # =========================================================
# #                   API LAYER
# # =========================================================
# def _fetch_product_raw(barcode: str) -> Optional[dict]:
#     """Запрос к OpenBeautyFacts API"""
#     try:
#         response = requests.get(
#             f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json",
#             timeout=5,
#         )
#         response.raise_for_status()
#         return response.json()
#
#     except requests.Timeout:
#         logger.warning("api_timeout", extra={"barcode": barcode})
#     except requests.RequestException:
#         logger.exception("api_request_failed", extra={"barcode": barcode})
#
#     return None
#
#
# def _parse_api_response(data: dict) -> Optional[OpenBeautyFactsResponse]:
#     """Валидация ответа API через Pydantic"""
#     try:
#         return OpenBeautyFactsResponse.model_validate(data)
#     except Exception:
#         logger.exception("api_response_validation_failed")
#         return None
#
#
# def _map_to_dto(barcode: str, data: OpenBeautyFactsResponse) -> ProductDTO:
#     """Маппинг API модели → DTO"""
#     product = data.product
#
#     dto_data = {
#         "barcode": barcode,
#         "name": product.product_name or "Неизвестно",
#         "brand": product.brands or "",
#         "category": product.categories or "",
#         "ingredients": product.ingredients_text_en or "",
#         "image_url": product.image_front_url,
#         "additional_info": {
#             "Упаковка": product.packaging or "",
#             "Вес": product.quantity or "",
#             "Страна": product.countries or "",
#         },
#     }
#
#     return ProductDTO.model_validate(dto_data)
#
#
# def get_cosmetic_info(barcode: str) -> Optional[ProductDTO]:
#     """Главный сервис получения продукта"""
#     raw_data = _fetch_product_raw(barcode)
#     if not raw_data:
#         return None
#
#     parsed = _parse_api_response(raw_data)
#     if not parsed:
#         return None
#
#     if parsed.status != 1:
#         logger.info("product_not_found", extra={"barcode": barcode})
#         return None
#
#     try:
#         dto = _map_to_dto(barcode, parsed)
#         logger.info("product_fetched", extra={"barcode": barcode})
#         return dto
#
#     except Exception:
#         logger.exception("dto_mapping_failed", extra={"barcode": barcode})
#         return None
#
#
# # =========================================================
# #                   BARCODE LAYER
# # =========================================================
# def read_barcodes_from_image(image_path: str) -> Generator[str, None, None]:
#     """Чтение штрих-кодов с изображения"""
#     pyzbar = _load_optional_dependency("pyzbar")
#     if not pyzbar:
#         return
#
#     try:
#         image = Image.open(image_path)
#     except Exception:
#         logger.exception("image_open_failed", extra={"path": image_path})
#         return
#
#     barcodes = pyzbar.pyzbar.decode(image)
#
#     for barcode in barcodes:
#         try:
#             yield barcode.data.decode("utf-8")
#         except Exception:
#             logger.warning("barcode_decode_failed")
#
#
# def scan_barcodes_from_camera() -> Generator[str, None, None]:
#     """Сканирование штрих-кодов с камеры"""
#     cv2 = _load_optional_dependency("cv2")
#     pyzbar = _load_optional_dependency("pyzbar")
#
#     if not cv2 or not pyzbar:
#         logger.info("camera_scan_unavailable")
#         return
#
#     cap = cv2.VideoCapture(0)
#
#     if not cap.isOpened():
#         logger.error("camera_not_available")
#         return
#
#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 logger.warning("camera_frame_read_failed")
#                 break
#
#             barcodes = pyzbar.pyzbar.decode(frame)
#
#             for barcode in barcodes:
#                 try:
#                     yield barcode.data.decode("utf-8")
#                 except Exception:
#                     logger.warning("barcode_decode_failed")
#
#             cv2.imshow("Barcode Scanner", frame)
#
#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break
#
#     finally:
#         cap.release()
#         cv2.destroyAllWindows()
#
#
# # =========================================================
# #                   APPLICATION LAYER
# # =========================================================
# def process_image(image_path: str):
#     """Обработка изображения"""
#     for barcode in read_barcodes_from_image(image_path):
#         logger.info("barcode_detected", extra={"barcode": barcode})
#
#         product = get_cosmetic_info(barcode)
#         if product:
#             logger.info("product_ready", extra={"barcode": barcode})
#             logger.debug("product_payload", extra={"payload": product.model_dump()})
#
#
# def process_camera():
#     """Обработка камеры"""
#     for barcode in scan_barcodes_from_camera():
#         logger.info("barcode_detected", extra={"barcode": barcode})
#
#         product = get_cosmetic_info(barcode)
#         if product:
#             logger.info("product_ready", extra={"barcode": barcode})
#
#
# # =========================================================
# #                   ENTRYPOINT
# # =========================================================
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#
#     # пример запуска
#     process_image("img_example/barcode.jpg")
#     # process_camera()

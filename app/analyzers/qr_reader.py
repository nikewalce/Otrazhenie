import requests
from PIL import Image
from app.schemas.products_schema import OpenBeautyFactsResponse
from app.schemas.product_dto import ProductDTO

def parse_api_response(data: dict) -> OpenBeautyFactsResponse | None:
    try:
        return OpenBeautyFactsResponse.model_validate(data)
    except Exception as e:
        print(f"Ошибка валидации API: {e}")
        return None

def read_barcode_from_image(image_path):
    # lazy imports для усиления устойчивости
    try:
        from pyzbar import pyzbar
    except ImportError:
        print("pyzbar/zbar не установлен, чтение штрих-кода недоступно")
        return
    image = Image.open(image_path)
    barcodes = pyzbar.decode(image)

    for barcode in barcodes:
        print("Штрих-код:", barcode.data.decode("utf-8"))
        product_info = get_cosmetic_info(barcode.data.decode("utf-8"))
        print("Информация о товаре:", product_info)


def scan_barcode():
    # lazy imports для усиления устойчивости
    try:
        import cv2
        from pyzbar import pyzbar
    except ImportError:
        print("OpenCV или pyzbar не установлены, сканирование с камеры недоступно")
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
            print("Информация о товаре:", product_info)

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
            timeout=5, # если API не ответил за 5 секунд — считаем, что он умер
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
        print(f"Ошибка API: {str(e)}")
        return None


if __name__ == "__main__":
    barcode = read_barcode_from_image("img_example/barcode.jpg")
    print(get_cosmetic_info(barcode))

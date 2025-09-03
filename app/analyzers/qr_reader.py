import cv2
import requests
from PIL import Image
from pyzbar import pyzbar


def read_barcode_from_image(image_path):
    image = Image.open(image_path)
    barcodes = pyzbar.decode(image)

    for barcode in barcodes:
        print("Штрих-код:", barcode.data.decode("utf-8"))
        product_info = get_cosmetic_info(barcode.data.decode("utf-8"))
        print("Информация о товаре:", product_info)


def scan_barcode():
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
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Выводим данные штрих-кода
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Получаем информацию о косметике
            product_info = get_cosmetic_info(barcode_data)
            print("Информация о товаре:", product_info)

        cv2.imshow("Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# def get_cosmetic_info(barcode):
#     # Попробуем несколько API для поиска косметики
#     apis = [
#         {"name": "Open Beauty Facts", "url": f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json"},
#         {"name": "Barcode Lookup (универсальный)",
#          "url": f"https://api.barcodelookup.com/v3/products?barcode={barcode}&formatted=y&key=ВАШ_API_КЛЮЧ"},
#     ]
#
#     for api in apis:
#         try:
#             response = requests.get(api["url"])
#             data = response.json()
#             if api["name"] == "Open Beauty Facts":
#                 if data.get("status") == 1:
#                     product = data.get("product", {})
#                     return {
#                         "Название": product.get("product_name", "Неизвестно"),
#                         "Бренд": product.get("brands", "Неизвестно"),
#                         "Категория": product.get("categories", "Неизвестно"),
#                         "Состав": product.get("ingredients_text_en", "Нет данных"),
#                         "Изображение": product.get("image_front_url", "Нет данных")
#                     }
#                 else:
#                     continue  # Пробуем следующий API
#
#             elif api["name"] == "Barcode Lookup (универсальный)":
#                 if data.get("products"):
#                     product = data["products"][0]
#                     return {
#                         "Название": product.get("product_name", "Неизвестно"),
#                         "Бренд": product.get("brand", "Неизвестно"),
#                         "Описание": product.get("description", "Нет данных"),
#                     }
#
#         except Exception as e:
#             print(f"Ошибка при запросе к {api['name']}: {e}")
#
#     return "Товар не найден в доступных базах."

def get_cosmetic_info(barcode):
    """Получает информацию о продукте по штрих-коду"""
    try:
        response = requests.get(
            f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json",
            timeout=5
        )
        data = response.json()
        if data.get("status") == 1:
            product = data.get("product", {})
            return {
                "barcode": barcode,
                "name": product.get("product_name", "Неизвестно"),
                "brand": product.get("brands", ""),
                "category": product.get("categories", ""),
                "ingredients": product.get("ingredients_text_en", ""),
                "image_url": product.get("image_front_url"),
                "additional_info": {
                    "Упаковка": product.get("packaging", ""),
                    "Вес": product.get("quantity", ""),
                    "Страна": product.get("countries", "")
                }
            }
        return None
    except Exception as e:
        print(f"Ошибка API: {str(e)}")
        return None

if __name__ == "__main__":
    barcode = read_barcode_from_image("img_example/barcode.jpg")
    print(get_cosmetic_info(barcode))
from flask import Flask, render_template, request, redirect, url_for, flash
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import csv
import os
from analyzers.qr_reader import get_cosmetic_info
from app.db import crud


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Словарь для хранения базы ингредиентов
INCI_DB = {}

def load_ingredients_database():
    """
    Загружает базу ингредиентов из CSV-файла 'analyzers/inci_data.csv' в глобальный словарь INCI_DB.
    Ключ — имя ингредиента в нижнем регистре, значение — вся строка из CSV в виде словаря.
    Если файл не найден, выводит предупреждение.
    """
    try:
        with open('analyzers/inci_data.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                INCI_DB[row['name'].strip().lower()] = row
    except FileNotFoundError:
        print("Warning: Ingredients database not found!")

load_ingredients_database()


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Главная страница.
    При GET-запросе рендерит index.html.
    При POST-запросе принимает состав продукта из формы и редиректит с этой информацией на эндпоинт results
    """
    if request.method == 'POST':
        composition = request.form.get('composition', '')
        # после отправки формы редиректим на /results
        return redirect(url_for('results', composition=composition))

    return render_template("index.html", active_tab='scanner')
@app.route("/results", methods=['GET'])
def results():
    """
    Страница с анализом состава.
    """
    composition = request.args.get('composition', '')

    ingredients = [i.strip().lower() for i in composition.split(",") if i.strip()]
    analysis = []

    for name in ingredients:
        data = INCI_DB.get(name, {
            'name': name,
            'function': 'Неизвестно',
            'safety_score': '?',
            'description': 'Не найден в базе данных'
        })
        analysis.append(data)

    return render_template("results.html",
                           composition=composition,
                           analysis=analysis,
                           active_tab='scanner')

@app.route("/handle-scan", methods=['POST'])
def handle_scan():
    """
    Обрабатывает загрузку изображения штрих-кода.
    Проверяет наличие файла, декодирует штрих-код из изображения,
    пытается получить информацию о продукте по штрих-коду.
    Если найден — показывает страницу product_info.html с данными.
    Если нет — возвращается обратно с сообщением об ошибке.
    """
    if 'barcode_image' not in request.files:
        flash("Файл не загружен", "error")
        return redirect(url_for('index'))

    file = request.files['barcode_image']
    if file.filename == '':
        flash("Файл не выбран", "error")
        return redirect(url_for('index'))

    try:
        barcode_data = decode_barcode(file.read())

        if not barcode_data:
            flash("Не удалось распознать штрих-код", "warning")
            return redirect(url_for('index'))

        product_info = get_cosmetic_info(barcode_data)

        if product_info:
            return render_template("product_info.html",
                                   product=product_info,
                                   active_tab='scanner')
        else:
            return render_template("index.html", alert_message="Продукт с таким штрих-кодом не найден",
                                   alert_type="warning")

    except Exception as e:
        flash(f"Ошибка при обработке: {e}", "error")
        return redirect(url_for('index'))


@app.route("/handle-search", methods=['POST'])
def handle_search():
    """
    Обрабатывает поиск продукта по введенному названию или штрих-коду в форме поиска.
    Если введённое значение — число (возможный штрих-код), пытается получить инфо о продукте.
    Если продукт найден — отображает product_info.html.
    Иначе — показывает предупреждение и возвращается на главную.
    """
    input_data = request.form.get('product_name', '').strip()

    if input_data.isdigit() and len(input_data) >= 8:
        try:
            product_info = get_cosmetic_info(input_data)

            if product_info:
                return render_template("product_info.html",
                                       product=product_info,
                                       active_tab='scanner')

            flash("Продукт с таким штрих-кодом не найден", "warning")
        except Exception as e:
            flash(f"Ошибка при поиске продукта: {str(e)}", "error")

    return redirect(url_for('index'))


@app.route("/manual-analysis", methods=['POST'])
def manual_analysis():
    """
    Обрабатывает ручной ввод состава продукта.
    Если состав не введён — показывает ошибку.
    Иначе — возвращается на главную страницу с переданным составом в параметрах URL (для возможного дальнейшего использования).
    """
    product_name = request.form.get('product_name', '').strip()
    composition = request.form.get('composition', '').strip()

    if not composition:
        flash("Пожалуйста, введите состав продукта", "error")
        return redirect(url_for('index'))

    return redirect(url_for('index', composition=composition))


def decode_barcode(image_data):
    """
    Принимает бинарные данные изображения.
    Декодирует штрих-код (или QR-код) из изображения с помощью OpenCV и pyzbar.
    Возвращает строковое значение распознанного кода или None, если код не найден.
    """
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)
    return barcodes[0].data.decode('utf-8') if barcodes else None


def lookup_product_by_barcode(barcode):
    """
    Заглушка для поиска продукта по штрих-коду.
    В реальном приложении здесь будет вызов к API или запрос к базе.
    Возвращает фиктивный продукт для тестирования.
    """
    return {'id': '123', 'name': 'Пример продукта', 'ingredients': 'aqua,parfum'}


def search_product_by_name(name):
    """
    Заглушка для поиска продукта по названию.
    В реальном приложении здесь будет запрос к базе данных.
    Возвращает фиктивный продукт для тестирования.
    """
    return {'id': '456', 'name': name, 'ingredients': 'aqua,glycerin'}


@app.route("/diary")
def diary():
    """
    Рендерит страницу дневника с фиктивным списком продуктов.
    """
    mock_products = [
        {
            "id": 1,
            "name": "Увлажняющий крем для лица",
            "brand": "Beauty Natural",
            "rating": "safe",
            "score": 8.5,
            "ingredients": 12,
            "risk_ingredients": 0
        },
        {
            "id": 2,
            "name": "Тональный крем SPF 30",
            "brand": "Glow Cosmetics",
            "rating": "moderate",
            "score": 6.2,
            "ingredients": 18,
            "risk_ingredients": 2
        }
    ]
    return render_template("diary.html", products=mock_products, active_tab='diary')


@app.route("/recommendations")
def recommendations():
    """
    Рендерит страницу рекомендаций.
    """
    return render_template("recommendations.html", active_tab='recommendations')


@app.route("/profile")
def profile():
    """
    Рендерит страницу профиля пользователя.
    """
    return render_template("profile.html", active_tab='profile')


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import csv
import os
from analyzers.qr_reader import get_cosmetic_info
from flask import flash

app = Flask(__name__)

# Загрузка базы ингредиентов
INCI_DB = {}


def load_ingredients_database():
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
    if request.method == 'POST':
        composition = request.form.get('composition', '')
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

    return render_template("index.html", active_tab='scanner')


@app.route("/handle-scan", methods=['POST'])
def handle_scan():
    if 'barcode_image' not in request.files:
        return redirect(url_for('index'))

    file = request.files['barcode_image']
    if file.filename == '':
        return redirect(url_for('index'))

    # Здесь будет обработка изображения
    print("Получено изображение для сканирования:", file.filename)
    return redirect(url_for('index'))


@app.route("/handle-search", methods=['POST'])
def handle_search():
    input_data = request.form.get('product_name', '').strip()

    # Проверяем, является ли ввод штрих-кодом (EAN-13 обычно 13 цифр)
    if input_data.isdigit() and len(input_data) >= 8:
        try:
            product_info = get_cosmetic_info(input_data)

            if product_info:
                # Если нашли продукт - рендерим страницу с информацией
                return render_template("product_info.html",
                                       product=product_info,
                                       active_tab='scanner')

            flash("Продукт с таким штрих-кодом не найден", "warning")
        except Exception as e:
            flash(f"Ошибка при поиске продукта: {str(e)}", "error")

    return redirect(url_for('index'))

@app.route("/manual-analysis", methods=['POST'])
def manual_analysis():
    product_name = request.form.get('product_name', '').strip()
    composition = request.form.get('composition', '').strip()

    if not composition:
        flash("Пожалуйста, введите состав продукта", "error")
        return redirect(url_for('index'))

    return redirect(url_for('index', composition=composition))

# Вспомогательные функции
def decode_barcode(image_data):
    """Декодирует штрих-код из изображения"""
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)
    return barcodes[0].data.decode('utf-8') if barcodes else None


def lookup_product_by_barcode(barcode):
    """Заглушка: поиск продукта по штрих-коду"""
    # Реализуйте подключение к API или вашей БД
    return {'id': '123', 'name': 'Пример продукта', 'ingredients': 'aqua,parfum'}


def search_product_by_name(name):
    """Заглушка: поиск продукта по названию"""
    # Реализуйте поиск в вашей базе данных
    return {'id': '456', 'name': name, 'ingredients': 'aqua,glycerin'}


@app.route("/diary")
def diary():
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
    return render_template("recommendations.html", active_tab='recommendations')


@app.route("/profile")
def profile():
    return render_template("profile.html", active_tab='profile')


if __name__ == "__main__":
    app.run(debug=True)
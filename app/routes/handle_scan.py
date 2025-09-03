from flask import Blueprint, render_template,redirect, request, url_for,flash
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
from app.analyzers.qr_reader import get_cosmetic_info

handle_scan_bp = Blueprint("handle_scan_bp", __name__)

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

@handle_scan_bp.route("/handle-scan", methods=['POST'], endpoint="handle_scan")
def handle_scan_page():
    """
    Обрабатывает загрузку изображения штрих-кода.
    Проверяет наличие файла, декодирует штрих-код из изображения,
    пытается получить информацию о продукте по штрих-коду.
    Если найден — показывает страницу product_info.html с данными.
    Если нет — возвращается обратно с сообщением об ошибке.
    """
    if 'barcode_image' not in request.files:
        flash("Файл не загружен", "error")
        return redirect(url_for('index_bp.index'))

    file = request.files['barcode_image']
    if file.filename == '':
        flash("Файл не выбран", "error")
        return redirect(url_for('index_bp.index'))

    try:
        barcode_data = decode_barcode(file.read())

        if not barcode_data:
            flash("Не удалось распознать штрих-код", "warning")
            return redirect(url_for('index_bp.index'))

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
        return redirect(url_for('index_bp.index'))

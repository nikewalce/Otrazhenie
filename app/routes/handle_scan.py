import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from flask import Blueprint, flash, redirect, render_template, url_for

from app.analyzers.qr_reader import get_cosmetic_info
from app.forms import ScanForm

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
    return barcodes[0].data.decode("utf-8") if barcodes else None


@handle_scan_bp.route("/handle-scan", methods=["GET", "POST"], endpoint="handle_scan")
def handle_scan_page():
    """
    Обрабатывает загрузку изображения штрих-кода.
    При GET-запросе показывает страницу сканирования.
    При POST-запросе проверяет наличие файла, декодирует штрих-код из изображения,
    пытается получить информацию о продукте по штрих-коду.
    Если найден — показывает страницу results.html с данными.
    Если нет — возвращается обратно с сообщением об ошибки.
    """
    form = ScanForm()

    if form.validate_on_submit():
        file = form.barcode_image.data
        try:
            barcode_data = decode_barcode(file.read())

            if not barcode_data:
                flash("Не удалось распознать штрих-код", "warning")
                return redirect(url_for("handle_scan_bp.handle_scan"))

            product_info = get_cosmetic_info(barcode_data)

            if product_info:
                return render_template(
                    "fullpage/product_info.html",
                    product=product_info,
                    active_tab="scanner",
                )
            else:
                flash("Продукт с таким штрих-кодом не найден", "warning")
                return redirect(url_for("handle_scan_bp.handle_scan"))

        except Exception as e:
            flash(f"Ошибка при обработке: {e}", "error")
            return redirect(url_for("handle_scan_bp.handle_scan"))

    return render_template("fullpage/scan.html", form=form, active_tab="scanner")

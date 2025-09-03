from flask import Blueprint, render_template,redirect, request, url_for,flash
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
from app.analyzers.qr_reader import get_cosmetic_info

handle_search_bp = Blueprint("handle_search_bp", __name__)


@handle_search_bp.route("/handle-search", methods=['POST'], endpoint='handle_search')
def handle_search_page():
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

    return redirect(url_for('index_bp.index'))

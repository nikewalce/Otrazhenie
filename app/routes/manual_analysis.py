from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


manual_analysis_bp = Blueprint("manual_analysis_bp", __name__, url_prefix="/manual-analysis")

@manual_analysis_bp.route("/manual-analysis", methods=['POST'], endpoint="manual_analysis")
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
        return redirect(url_for('index_bp.index'))

    return redirect(url_for('index_bp.index', composition=composition))

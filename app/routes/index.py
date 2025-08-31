from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


index_bp = Blueprint("index_bp", __name__, url_prefix="/")

@index_bp.route("/", methods=['GET', 'POST'], endpoint="index")
def index_page():
    """
    Главная страница.
    При GET-запросе рендерит index.html.
    При POST-запросе принимает состав продукта из формы и редиректит с этой информацией на эндпоинт results
    """
    if request.method == 'POST':
        composition = request.form.get('composition', '')
        # после отправки формы редиректим на /results
        return redirect(url_for('results_bp.results', composition=composition))

    return render_template("index.html", active_tab='scanner')

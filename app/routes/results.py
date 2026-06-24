from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from app.db import crud
from app.forms import CompositionForm
import logging
results_bp = Blueprint("results_bp", __name__)

logger = logging.getLogger(__name__)

def load_ingredients_database():
    """
    Подгружаем данные из бд и преобразуем в словарь
    Ключ — имя ингредиента в нижнем регистре, значение — словарь из данных бд
    Если ошибка, выводит предупреждение
    """
    try:
        db_data = crud.OtrazhenieDB().select_all_ingredients_with_names()
        logger.info("Загрузка базы данных ингредиентов")
        ingredients_dict = {}
        for row in db_data:
            db_dict = {
                "name": row[1],
                "function": row[2],
                "safety_score": row[3],
                "description": row[4],
            }
            ingredients_dict[row[1].lower()] = db_dict
        logger.info(
            "База данных ингредиентов успешно загружена: %s элементов",
            len(ingredients_dict),
        )
        return ingredients_dict
    except FileNotFoundError:
        logger.exception("Не удалось загрузить базу данных ингредиентов")
        return {}


def analyze_composition(composition: str):
    """
    Возвращает список словарей с данными по каждому ингредиенту из строки состава.
    Если ингредиент отсутствует в БД — заполняем placeholder-значениями.
    """
    normalized_ingredients = [
        i.strip().lower() for i in composition.split(",") if i.strip()
    ]
    logger.info(
        "Анализ состава, количество ингредиентов=%s",
        len(normalized_ingredients)
    )
    db_data = load_ingredients_database() or {}
    analysis_result = []
    for ingredient_name in normalized_ingredients:
        analysis_result.append(
            db_data.get(
                ingredient_name,
                {
                    "name": ingredient_name,
                    "function": "Неизвестно",
                    "safety_score": "?",
                    "description": "Не найден в базе данных",
                },
            )
        )
    logger.info("Анализ состава завершен")
    return analysis_result


@results_bp.route("/analyze", methods=["POST"])
def analyze():
    form = CompositionForm()

    if form.validate_on_submit():
        logger.info("Отправлена валидная форма состава")
        return redirect(
            url_for("results_bp.results", composition=form.composition.data)
        )

    # если форма невалидна — вернуть на главную
    logger.warning("Отправлена невалидная форма состава")
    return redirect(url_for("index_bp.index"))


@results_bp.route("/results", methods=["GET"], endpoint="results")
def results_page():
    """
    Страница с анализом состава
    Получаем данные из формы composition, подгружаем данные из бд,
    помещаем их в список и рендерим result.html
    """
    composition = (
        request.form.get("composition")  # сначала пробуем из формы (POST)
        or request.args.get("composition")  # если нет — берём из query (GET)
        or ""  # если нигде нет — пустая строка
    )
    logger.info(
        "Запрошена страница результатов, длина состава=%s",
        len(composition)
    )
    if not composition:
        logger.warning("На странице результатов отображается пустой состав")
    analysis = analyze_composition(composition)
    # return render_template("results.html",
    return render_template(
        "fullpage/results.html",
        composition=composition,
        analysis=analysis,
        active_tab="scanner",
    )


@results_bp.route("/add_unknown", methods=["POST"])
def add_unknown():
    data = request.get_json()
    name = data.get("name")
    function_ru = data.get("function_ru")
    function_en = data.get("function_en")
    description_category = data.get("description_category")
    description = data.get("description")
    safety_score = data.get("safety_score")

    logger.info("Запрос на добавление неизвестного ингредиента: %s", name)
    if not name or not safety_score:
        logger.warning(
            "Отсутствуют обязательные поля при добавлении ингредиента: has_name=%s, has_safety_score=%s",
            bool(name),
            bool(safety_score),
        )
        return jsonify(success=False, message="Не хватает данных"), 400
    try:
        new_ing = crud.OtrazhenieDB()
        new_ing.add_ingredient_with_category(
            name=name,
            category_name_ru=function_ru,
            category_name_en=function_en,
            description_category=description_category,
            safety_score=safety_score,
            description=description,
        )
        logger.info("Ингредиенты успешно добавлены: %s", name)
        return jsonify(success=True, message=f"{name} добавлен")
    except:
        logger.exception("Ошибка в добавлении ингредиента: %s", name)
        return jsonify(success=False, message="Ошибка сервера"), 500


@results_bp.route(
    "/ingredient/<string:name>", methods=["GET"], endpoint="ingredient_detail"
)
def ingredient_detail(name: str):
    """
    Детальная страница ингредиента: описание, функция, рейтинг безопасности.
    """
    db_data = load_ingredients_database() or {}
    key = (name or "").strip().lower()
    logger.info("Запрошенная информация об ингредиенте: %s", key)

    data = db_data.get(
        key,
        {
            "name": name,
            "function": "Неизвестно",
            "safety_score": "?",
            "description": "Не найден в базе данных",
        },
    )
    if data.get("function") == "Неизвестно":
        logger.warning("Ингредиент не найден: %s", key)
    # Рендерим fullpage-шаблон с деталями
    return render_template(
        "fullpage/ingredient_detail.html", ingredient=data, active_tab="scanner"
    )

from app.db import crud
from flask import render_template, request, Blueprint, jsonify

results_bp = Blueprint("results_bp", __name__)

def load_ingredients_database():
    """
    Подгружаем данные из бд и преобразуем в словарь
    Ключ — имя ингредиента в нижнем регистре, значение — словарь из данных бд
    Если ошибка, выводит предупреждение
    """
    try:
        db_data = crud.OtrazhenieDB().select_all_ingredients_with_names()
        ingredients_dict = {}
        for row in db_data:
            db_dict = {'name': row[1], 'function': row[2], 'safety_score': row[3], 'description': row[4]}
            ingredients_dict[row[1].lower()] = db_dict
        return ingredients_dict
    except FileNotFoundError:
        print("Warning: Ingredients database not found!")

@results_bp.route("/results", methods=['GET', 'POST'], endpoint='results')
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

    ingredients = [i.strip().lower() for i in composition.split(",") if i.strip()]
    analysis = []
    db_data = load_ingredients_database()
    for name in ingredients:
        data = db_data.get(name, {
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


@results_bp.route("/add_unknown", methods=["POST"])
def add_unknown():
    data = request.get_json()
    name = data.get("name")
    function_ru = data.get("function_ru")
    function_en = data.get("function_en")
    description_category = data.get("description_category")
    description = data.get("description")
    safety_score = data.get("safety_score")

    if not name or not safety_score:
        return jsonify(success=False, message="Не хватает данных"), 400

    new_ing = crud.OtrazhenieDB()
    new_ing.add_ingredient_with_category(
        name=name,
        category_name_ru=function_ru,
        category_name_en=function_en,
        description_category=description_category,
        safety_score=safety_score,
        description=description,
    )
    return jsonify(success=True, message=f"{name} добавлен")

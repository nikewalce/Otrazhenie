# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import csv
# import os
#
# app = FastAPI()
#
# # Подключение статических файлов и шаблонов
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
# templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
#
# # Загрузка базы ингредиентов (CSV)
# INCI_DB = {}
# with open(os.path.join(BASE_DIR, "analyzers/inci_data.csv"), encoding='utf-8') as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         INCI_DB[row['name'].strip().lower()] = row
#
# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse("home.html", {"request": request})
#
# @app.post("/analyze", response_class=HTMLResponse)
# def analyze(request: Request, composition: str = Form(...)):
#     ingredients = [i.strip().lower() for i in composition.split(",") if i.strip()]
#     analysis = []
#
#     for name in ingredients:
#         data = INCI_DB.get(name, {
#             'name': name,
#             'function': 'Unknown',
#             'safety_score': '?',
#             'description': 'Not found in database'
#         })
#         analysis.append(data)
#
#     return templates.TemplateResponse("results.html", {
#         "request": request,
#         "composition": composition,
#         "analysis": analysis
#     })

from flask import Flask, render_template, request
import csv
import os

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
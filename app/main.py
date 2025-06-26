from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv
import os

app = FastAPI()

# Подключение статических файлов и шаблонов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Загрузка базы ингредиентов (CSV)
INCI_DB = {}
with open(os.path.join(BASE_DIR, "analyzers/inci_data.csv"), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        INCI_DB[row['name'].strip().lower()] = row

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
def analyze(request: Request, composition: str = Form(...)):
    ingredients = [i.strip().lower() for i in composition.split(",") if i.strip()]
    analysis = []

    for name in ingredients:
        data = INCI_DB.get(name, {
            'name': name,
            'function': 'Unknown',
            'safety_score': '?',
            'description': 'Not found in database'
        })
        analysis.append(data)

    return templates.TemplateResponse("results.html", {
        "request": request,
        "composition": composition,
        "analysis": analysis
    })

# 📁 Структура проекта
```
Otrazhenie/  
│  
├── app/  
│   ├── main.py           # FastAPI app  
│   ├── models.py         # SQLAlchemy модели
│   ├── database.py       # Подключение к БД
│   ├── crud.py           # Логика запросов
│   ├── templates/        # HTML-шаблоны
│   │   │── home.html     # Стартовая html-страница
│   │   └── results.html  # Результаты анализа состава
│   ├── static/           # CSS/JS
│   └── analyzers/        # Анализ состава
│       └── inci_data.csv # База ингредиентов
│
├── requirements.txt
├── README.md
```
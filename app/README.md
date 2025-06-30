# 📁 Структура проекта
```
otrazhenie/
│
├── app.py # Основное Flask-приложение
│
├── analyzers/ # Базы данных
│ └── inci_data.csv # База ингредиентов (CSV)
│
├── static/ # Статические файлы
│ └── css/
│      └── style.css # Основные стили
│
├── templates/ # Шаблоны Jinja2
│   ├── base.html # Базовый шаблон
│   ├── index.html # Главная страница (сканер)
│   ├── results.html # Результаты анализа
│   ├── diary.html # Косметический дневник
│   ├── recommendations.html # Рекомендации
│   └── profile.html # Профиль пользователя
│
├── requirements.txt # Зависимости Python
└── README.md # Документация
```
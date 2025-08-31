# 📁 Структура проекта
```
Otrazhenie/
│
├── .gitignore # Файлы и папки, игнорируемые Git
├── poetry.lock # Файл блокировки зависимостей Poetry
├── pyproject.toml # Конфигурация проекта, зависимости
├── README.md # Основная документация проекта
├── TODO.md # Список задач и идей
│
├── app/ # Основной пакет приложения
    ├── __init__.py # Инициализация Flask, регистрация blueprints
    ├── main.py # Точка входа приложения
    ├── README.md # Документация внутри приложения
    ├── schemas.py # Схемы данных (Pydantic)
    ├── .env # Переменные окружения
    │
    ├── analyzers/ # Логика анализа и распознавания
    │   ├── __init__.py
    │   ├── qr_reader.py # Чтение QR/штрих-кодов
    │   └── img_example/ # Примеры изображений
    │       ├── barcode.jpg
    │       ├── H&S.png
    │       ├── persavon.png
    │       ├── Без имени.png
    │       ├── Без имени1.png
    │       └── __init__.py
    │
    ├── db/ # Работа с базой данных
    │   ├── __init__.py
    │   ├── crud.py # Create/Read/Update/Delete
    │   ├── csv_to_db.py # Загрузка данных из CSV
    │   ├── models.py # SQLAlchemy модели
    │   ├── session.py # Сессии базы данных
    │   └── csv_files/ # CSV с данными
    │       ├── inci_data.csv
    │       ├── ingredients.csv
    │       ├── ingredient_categories.csv
    │       └── __init__.py
    │
    ├── routes/ # Маршруты/эндпоинты
    │   ├── __init__.py
    │   ├── auth.py # Регистрация и авторизация
    │   ├── index.py # Главная страница
    │   ├── handle_scan.py # Обработка сканирования штрих-кодов
    │   ├── handle_search.py # Поиск продуктов
    │   ├── results.py # Вывод результатов поиска
    │   ├── diary.py # Дневник пользователя
    │   ├── recommendations.py # Рекомендации
    │   ├── profile.py # Профиль пользователя
    │   └── manual_analysis.py # Ручной анализ и ввод
    │
    ├── services/ # Сервисы бизнес-логики
    │   ├── __init__.py
    │   └── user_service.py # Работа с пользователем
    │
    ├── static/ # Статические файлы
    │   └── css/style.css
    │
    └── templates/ # HTML-шаблоны
        ├── base.html # Базовый шаблон
        ├── index.html # Главная страница
        ├── manual_input.html # Ручной ввод продукта
        ├── product_info.html # Информация о продукте
        ├── profile.html # Профиль пользователя
        ├── recommendations.html # Рекомендации
        ├── results.html # Результаты поиска
        └── auth/register.html # Регистрация
```
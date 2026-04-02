FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем pyproject.toml и poetry.lock (если есть)
COPY pyproject.toml .

# Устанавливаем зависимости через PIP (PEP 621)
RUN pip install --no-cache-dir .

# Копируем проект
COPY . .

# Запускаем Flask-приложение
CMD ["python", "app/main.py"]

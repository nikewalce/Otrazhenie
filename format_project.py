#!/usr/bin/env python3
"""
Скрипт для автоформатирования и проверки всего Django проекта:
- Black → автоформатирование
- isort → сортировка импортов
- Ruff → проверка стиля (PEP8)
Работает на Windows и Linux
"""

import subprocess
import sys

# Список инструментов
tools = ["black", "isort", "ruff"]


# Функция установки инструментов
def install_tools():
    for tool in tools:
        print(f"Устанавливаем {tool}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", tool], check=True
        )


# Функция форматирования кодa
def format_code():
    print("\n=== Форматируем код с помощью isort ===")
    subprocess.run([sys.executable, "-m", "isort", "."], check=True)

    print("\n=== Форматируем код с помощью black ===")
    subprocess.run([sys.executable, "-m", "black", "."], check=True)


# Функция проверки стиля
def check_style():
    print("\n=== Проверка кода на PEP8 с помощью ruff ===")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."],
            capture_output=True,
            text=True,
            encoding="utf-8",  # Явно указываем кодировку UTF-8
            errors="replace",  # Заменяем проблемные символы вместо ошибки
        )
        print(result.stdout)
        if result.returncode == 0:
            print("\n✅ Стиль кода соответствует PEP8!")
        else:
            print("\n⚠️ Обнаружены ошибки стиля!")
    except UnicodeDecodeError as e:
        print(f"\n❌ Ошибка декодирования: {e}")
        print("Попробуйте запустить ruff вручную в терминале:")
        print("python -m ruff check .")


# Главная функция
def main():
    print("=== Подготовка проекта к PEP8 ===")
    install_tools()
    format_code()
    check_style()
    print("\n=== Готово! Проект отформатирован и проверен ===")


if __name__ == "__main__":
    main()

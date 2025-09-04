from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


diary_bp = Blueprint("diary_bp", __name__)

@diary_bp.route("/diary", endpoint="diary")
def diary():
    """
    Рендерит страницу дневника с фиктивным списком продуктов.
    """
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
    #return render_template("diary.html", products=mock_products, active_tab='diary')
    return render_template("fullpage/diary.html", products=mock_products, active_tab='diary')


from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


recommendations_bp = Blueprint("recommendations_bp", __name__)

@recommendations_bp.route("/recommendations", endpoint="recommendations")
def recommendations():
    """
    Рендерит страницу рекомендаций.
    """
    #return render_template("recommendations.html", active_tab='recommendations')
    return render_template("fullpage/recommendations.html", active_tab='recommendations')

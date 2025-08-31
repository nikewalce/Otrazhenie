from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


profile_bp = Blueprint("profile_bp", __name__, url_prefix="/profile")

@profile_bp.route("/profile", endpoint="profile")
def profile():
    """
    Рендерит страницу профиля пользователя.
    """
    return render_template("profile.html", active_tab='profile')

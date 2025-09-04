from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
#from werkzeug.security import generate_password_hash, check_password_hash#
#from app import db

profile_bp = Blueprint("profile_bp", __name__)

@profile_bp.route("/profile", endpoint="profile")
@login_required
def profile():
    """
    Рендерит страницу профиля пользователя.
    """
    #return render_template("profile.html", active_tab='profile')
    #return render_template("fullpage/profile.html", active_tab='profile')
    return render_template("fullpage/profile.html", active_tab='profile', current_user=current_user)

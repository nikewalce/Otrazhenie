from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.db.crud import OtrazhenieDB

auth_bp = Blueprint("auth_bp", __name__)
db = OtrazhenieDB()

@auth_bp.route("/register", methods=["GET", "POST"])
def auth_register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if db.get_user_by_email(email):
            flash("Такой email уже зарегистрирован", "error")
            return redirect(url_for("auth_bp.auth_register"))

        db.create_user(username, email, password)

        flash("Регистрация успешна!", "success")
        return redirect(url_for("auth_bp.auth_login"))

    return render_template("fullpage/auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def auth_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if db.verify_user_password(email, password):
            # Получаем пользователя для создания сессии
            user = db.get_user_by_email(email)
            if user:
                login_user(user, remember=True)
                flash("Вы успешно вошли!", "success")
                return redirect(url_for("profile_bp.profile"))  # на страницу профиля
        else:
            flash("Неправильный email или пароль", "error")
            return redirect(url_for("auth_bp.auth_login"))

    return render_template("fullpage/auth/login.html")

@auth_bp.route("/logout")
@login_required
def auth_logout():
    """Выход пользователя из системы"""
    logout_user()
    flash("Вы успешно вышли из системы!", "success")
    return redirect(url_for("index_bp.index"))

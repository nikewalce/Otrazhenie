from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app.db.crud import OtrazhenieDB
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth_bp", __name__)
db = OtrazhenieDB()


@auth_bp.route("/register", methods=["GET", "POST"])
def auth_register():
    form = RegistrationForm()

    if form.validate_on_submit():  # Проверяет POST и валидность формы
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if db.get_user_by_email(email):
            flash("Такой email уже зарегистрирован", "error")
            return redirect(url_for("auth_bp.auth_register"))

        db.create_user(username, email, password)
        flash("Регистрация успешна!", "success")
        return redirect(url_for("auth_bp.auth_login"))

    return render_template("fullpage/auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def auth_login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if db.verify_user_password(email, password):
            user = db.get_user_by_email(email)
            if user:
                login_user(user, remember=True)
                flash("Вы успешно вошли!", "success")
                return redirect(url_for("profile_bp.profile"))
        else:
            flash("Неправильный email или пароль", "error")
            return redirect(url_for("auth_bp.auth_login"))

    return render_template("fullpage/auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def auth_logout():
    """Выход пользователя из системы"""
    logout_user()
    flash("Вы успешно вышли из системы!", "success")
    return redirect(url_for("index_bp.index"))

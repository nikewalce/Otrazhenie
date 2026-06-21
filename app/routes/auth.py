from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user
from pydantic import ValidationError as PydanticValidationError
import logging
# Кастомная ошибка бизнес-валидации (уровень сервиса)
from app.exceptions.validation import ValidationError

# WTForms формы (UI-слой)
from app.forms import LoginForm, RegistrationForm

# Сервисный слой (вся бизнес-логика там, НЕ во view)
from app.services.user_service import user_service

# Blueprint — это модуль маршрутов Flask
# Зачем:
# - разделение приложения на модули
# - масштабируемость (auth, profile, admin и т.д.)
auth_bp = Blueprint("auth_bp", __name__)

logger = logging.getLogger(__name__)
# =========================================================
#                 РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
# =========================================================
@auth_bp.route("/register", methods=["GET", "POST"])
def auth_register():
    """
    View слой регистрации пользователя

    - Flask view НЕ содержит бизнес-логики
    - только:
        1. получение данных формы
        2. вызов service
        3. обработка результата
        4. возврат шаблона/редиректа
    """

    # WTForms форма (валидация на уровне UI)
    form = RegistrationForm()

    # Проверяет:
    # - POST запрос
    # - CSRF токен
    # - валидность полей формы
    if form.validate_on_submit():

        try:
            # Передаём данные в сервисный слой
            # Важно: view НЕ знает как создаётся пользователь
            logger.info(
                "Попытка регистрации пользователя. username=%s, email=%s", form.username.data, form.email.data
            )

            user = user_service.register_user(
                {
                    "username": form.username.data,
                    "email": form.email.data,
                    "password": form.password.data,
                }
            )
            logger.info(
                "Пользователь успешно зарегистрирован. id=%s", user.id)
            # flash — механизм уведомлений Flask (хранится в session)
            flash("Регистрация успешна!", "success")

            # redirect после POST — паттерн PRG (Post/Redirect/Get)
            return redirect(url_for("auth_bp.auth_login"))

        except (ValidationError, PydanticValidationError) as e:
            """
            Обработка ошибок:
            - ValidationError → бизнес-логика (дубликаты, правила)
            - PydanticValidationError → формат данных

            - сервис не знает про flash / UI
            - view отвечает за отображение ошибок
            """
            logger.exception(
                "Ошибка регистрации пользователя. username=%s, email=%s", form.username.data, form.email.data)
            # e.errors() — стандарт Pydantic (dict ошибок по полям)
            for field, msg in e.errors.items():

                # non_field → общие ошибки (не привязаны к полю)
                if field == "non_field":
                    flash(msg, "error")
                else:
                    flash(msg, "error")


    # GET запрос или невалидная форма → просто рендерим страницу
    return render_template("fullpage/auth/register.html", form=form)


# =========================================================
#                 ЛОГИН ПОЛЬЗОВАТЕЛЯ
# =========================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def auth_login():
    """
    Авторизация пользователя

    Поток:
    1. форма → email/password
    2. сервис проверяет пользователя
    3. Flask-Login кладёт пользователя в session
    """

    form = LoginForm()

    if form.validate_on_submit():

        # Вся логика проверки находится в service слое
        user = user_service.authenticate_user(form.email.data, form.password.data)

        if user:
            logger.info("Пользователь авторизовался с данными: \nлогин: %s\nпочта: %s", user.username, user.email)
            # login_user:
            # - сохраняет user_id в session
            # - активирует Flask-Login контекст пользователя
            # - позволяет использовать current_user
            login_user(user, remember=True)

            flash("Вы успешно вошли!", "success")

            # После логина обычно редирект на профиль
            return redirect(url_for("profile_bp.profile"))

        else:
            logger.info("Пользователь %s ввел неверные данные или такого пользователя не существует", form.email.data)
            # Неправильные данные → не создаём session
            flash("Неправильный email или пароль", "error")

            # возвращаем ту же страницу с ошибкой
            return render_template("fullpage/auth/login.html", form=form)

    # GET запрос → просто форма
    return render_template("fullpage/auth/login.html", form=form)


# =========================================================
#                 ВЫХОД ИЗ СИСТЕМЫ
# =========================================================
@auth_bp.route("/logout")
@login_required
def auth_logout():
    """
    Logout пользователя

    login_required:
    - защищает маршрут
    - доступ только авторизованным пользователям

    logout_user:
    - очищает session
    - удаляет current_user
    """

    logout_user()
    logger.info("Пользователь вышел из системы")
    flash("Вы успешно вышли из системы!", "success")

    # после выхода обычно отправляют на главную
    return redirect(url_for("index_bp.index"))

from decouple import UndefinedValueError, config
from app.core.logging_config import setup_logging
from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
import logging

from app.routes.auth import auth_bp
from app.routes.diary import diary_bp
from app.routes.handle_scan import handle_scan_bp
from app.routes.handle_search import handle_search_bp
from app.routes.index import index_bp
from app.routes.manual_analysis import manual_analysis_bp
from app.routes.profile import profile_bp
from app.routes.recommendations import recommendations_bp
from app.routes.results import results_bp

# Защита от CSRF (Cross-Site Request Forgery — «Межсайтовая подделка запроса»)
# Любое представление, использующее FlaskForm для обработки запроса, уже защищено от CSRF-атак
# Если у вас есть представления, которые не используют FlaskForm или не выполняют AJAX-запросы,
# используйте предоставленное расширение CSRF для защиты и этих запросов https://flask-wtf.readthedocs.io/en/0.15.x/csrf/
# включает защиту от CSRF-атак для всего приложения Flask
csrf = CSRFProtect()

# Инициализируем LoginManager
login_manager = LoginManager()

logger = logging.getLogger(__name__)

def create_app():
    # инициализация логирования на старте Flask-приложения,
    # чтобы все модули получали одинаковое поведение логов автоматически при запуске приложения
    setup_logging()
    app = Flask(__name__)
    # устанавливаем секретный ключ, если его нет, вызываем исключение RuntimeError
    try:
        SECRET_KEY = config("SECRET_KEY")
    except UndefinedValueError:
        raise RuntimeError(
            "SECRET_KEY не установлен! Установите его в .env или в переменной среды (environment variables)"
        )
    app.config["SECRET_KEY"] = SECRET_KEY

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        logger.warning("CSRF validation failed")
        flash("Сессия истекла или неверный CSRF токен. Повторите попытку.", "error")
        return redirect(url_for("index_bp.index")), 400

    # ленивое использование CSRFProtect, включаем CSRF защиту
    csrf.init_app(app)

    # Настраиваем Flask-Login
    login_manager.init_app(app)
    # если пользователь не авторизован и заходит на @login_required его редиректит на /login
    login_manager.login_view = "auth_bp.auth_login"
    login_manager.login_message = (
        "Пожалуйста, войдите в систему для доступа к этой странице."
    )
    login_manager.login_message_category = "info"

    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(handle_scan_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(handle_search_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(manual_analysis_bp)
    return app


@login_manager.user_loader
def load_user(user_id):
    """Функция для загрузки пользователя по ID (требуется для Flask-Login)
    Flask-Login работает так:

    Он хранит user_id в session (cookie)
    На каждый запрос:
    берет user_id из сессии
    вызывает load_user(user_id)
    получает пользователя
    кладёт в current_user
    """
    from app.db.crud import OtrazhenieDB

    db = OtrazhenieDB()

    # 1. защита от повреждённого session / атаки / мусора
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        logger.warning(
            "FLASK_LOGIN: некорректный user_id в session"
        )
        return None

    # 2. получаем пользователя
    user = db.get_user_by_id(user_id_int)

    # 3. пользователь удалён / не существует
    if not user:
        logger.info(
            "FLASK_LOGIN: пользователь не найден в БД, user_id=%s",
            user_id_int
        )
        return None

    return user

from decouple import UndefinedValueError, config
from flask import CSRFError, Flask, flash, redirect, url_for
from flask_login import LoginManager
from flask_wtf import CSRFProtect

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


def create_app():
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
        flash("Сессия истекла или неверный CSRF токен. Повторите попытку.", "error")
        return redirect(url_for("index_bp.index")), 400

    # ленивое использование CSRFProtect, включаем CSRF защиту
    csrf.init_app(app)

    # Настраиваем Flask-Login
    login_manager.init_app(app)
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
    """Функция для загрузки пользователя по ID (требуется для Flask-Login)"""
    from app.db.crud import OtrazhenieDB

    db = OtrazhenieDB()
    return db.get_user_by_id(int(user_id))

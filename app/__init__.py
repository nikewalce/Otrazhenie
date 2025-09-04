from flask import Flask
from decouple import config
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

from app.routes.auth import auth_bp
from app.routes.handle_scan import handle_scan_bp
from app.routes.handle_search import handle_search_bp
from app.routes.index import index_bp
from app.routes.results import results_bp
from app.routes.diary import diary_bp
from app.routes.recommendations import recommendations_bp
from app.routes.profile import profile_bp
from app.routes.manual_analysis import manual_analysis_bp

#csrf = CSRFProtect()

# Инициализируем LoginManager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # Используем значение по умолчанию для SECRET_KEY если переменная окружения не установлена
    try:
        app.config["SECRET_KEY"] = config("SECRET_KEY")
    except:
        app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    #csrf.init_app(app)  # включаем CSRF защиту
    
    # Настраиваем Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.auth_login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
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

from flask import Flask
from decouple import config
from app.routes.auth import auth_bp
from app.routes.handle_scan import handle_scan_bp
from app.routes.handle_search import handle_search_bp
from app.routes.index import index_bp
from app.routes.results import results_bp
from app.routes.diary import diary_bp
from app.routes.recommendations import recommendations_bp
from app.routes.profile import profile_bp
from app.routes.manual_analysis import manual_analysis_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = config("SECRET_KEY")
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

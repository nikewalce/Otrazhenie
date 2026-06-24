from flask import Blueprint, render_template
from flask_login import current_user
import logging
from app.forms import CompositionForm, ScanForm, SearchForm

index_bp = Blueprint("index_bp", __name__, url_prefix="/")

logger = logging.getLogger(__name__)

@index_bp.route("/", methods=["GET"], endpoint="index")
def index_page():
    composition_form = CompositionForm()
    search_form = SearchForm()
    scan_form = ScanForm()
    logger.debug("Главная страница загружена")
    return render_template(
        "fullpage/index.html",
        composition_form=composition_form,
        search_form=search_form,
        scan_form=scan_form,
        current_user=current_user,
    )

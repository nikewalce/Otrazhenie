from flask import Blueprint, render_template
from flask_login import current_user
from app.forms import CompositionForm, SearchForm, ScanForm

index_bp = Blueprint("index_bp", __name__, url_prefix="/")

@index_bp.route("/", methods=['GET'], endpoint="index")
def index_page():
    composition_form = CompositionForm()
    search_form = SearchForm()
    scan_form = ScanForm()

    return render_template(
        "fullpage/index.html",
        composition_form=composition_form,
        search_form=search_form,
        scan_form=scan_form,
        current_user=current_user
    )

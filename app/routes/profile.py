from flask import Blueprint, render_template
from flask_login import current_user, login_required
import logging
profile_bp = Blueprint("profile_bp", __name__)

logger = logging.getLogger(__name__)

@profile_bp.route("/profile", endpoint="profile")
@login_required
def profile():
    """
    Рендерит страницу профиля пользователя.
    """
    logger.debug("Загрузка профиля")
    # return render_template("profile.html", active_tab='profile')
    # return render_template("fullpage/profile.html", active_tab='profile')
    return render_template(
        "fullpage/profile.html", active_tab="profile", current_user=current_user
    )

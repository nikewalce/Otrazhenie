from flask import Blueprint, render_template
import logging
recommendations_bp = Blueprint("recommendations_bp", __name__)

logger = logging.getLogger(__name__)

@recommendations_bp.route("/recommendations", endpoint="recommendations")
def recommendations():
    """
    Рендерит страницу рекомендаций.
    """
    logger.info("Загрузка страницы рекомендации")
    # return render_template("recommendations.html", active_tab='recommendations')
    return render_template(
        "fullpage/recommendations.html", active_tab="recommendations"
    )

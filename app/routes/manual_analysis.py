from flask import Blueprint, flash, redirect, request, url_for
import logging
manual_analysis_bp = Blueprint("manual_analysis_bp", __name__)

logger = logging.getLogger(__name__)

@manual_analysis_bp.route(
    "/manual-analysis", methods=["POST"], endpoint="manual_analysis"
)
def manual_analysis():
    """
    Обрабатывает ручной ввод состава продукта.
    Если состав не введён — показывает ошибку.
    Иначе — возвращается на главную страницу с переданным составом в параметрах URL (для возможного дальнейшего использования).
    """
    # product_name = request.form.get("product_name", "").strip()
    composition = request.form.get("composition", "").strip()
    logger.info("Получен запрос на ручной анализ")
    if not composition:
        logger.warning("Пустой ввод при ручном анализе")
        flash("Пожалуйста, введите состав продукта", "error")
        return redirect(url_for("index_bp.index"))
    logger.info(
        "Получен состав на ручной анализ (длина=%s символов)",
        len(composition)
    )
    return redirect(url_for("index_bp.index", composition=composition))

from flask import Blueprint, render_template, request

from app.forms import CompositionForm, ScanForm, SearchForm
from app.services.product_lookup_service import get_product_info_from_api
import logging

logger = logging.getLogger(__name__)
handle_search_bp = Blueprint("handle_search_bp", __name__)


@handle_search_bp.route("/handle-search", methods=["POST"], endpoint="handle_search")
def handle_search_page():
    """
    Обрабатывает поиск продукта по введенному названию или штрих-коду в форме поиска.
    Если введённое значение — число (возможный штрих-код), пытается получить инфо о продукте.
    Если продукт найден — отображает product_info.html.
    Иначе — показывает предупреждение и возвращается на главную.
    """
    input_data = request.form.get("product_name", "").strip()
    error_message = None
    logger.info("Получен запрос на поиск: input=%s", input_data)
    if not input_data:
        error_message = "Введите название продукта"
        logger.warning("Пустой ввод поиска")
    elif not input_data.isdigit():
        error_message = "Штрих-код должен содержать только числа"
        logger.warning("Неверный формат штрих-кода: не цифры (%s)", input_data)
    elif len(input_data) < 8:
        error_message = "Длина штрих-кода должна быть не менее 8"
        logger.warning("Слишком короткий штрих-код: %s", input_data)
    else:
        try:
            product_info = get_product_info_from_api(input_data)
            if product_info:
                logger.info(
                    "Продукт найден по штрих-коду=%s",
                    input_data
                )
                return render_template(
                    "fullpage/product_info.html",
                    product=product_info.model_dump(),  # преобразуем pydantic модель в dict
                    active_tab="scanner",
                )
            else:
                error_message = "Продукт с таким штрих-кодом не найден"
                logger.warning(
                    "Продукт не найден по штрих-коду=%s",
                    input_data
                )
        except Exception as e:
            logger.exception("Ошибка при поиске продукта")
            error_message = "Ошибка при поиске продукта"
    composition_form = CompositionForm()
    search_form = SearchForm()
    scan_form = ScanForm()
    return render_template(
        "fullpage/index.html",
        composition_form=composition_form,
        search_form=search_form,
        scan_form=scan_form,
        error_message=error_message,
    )

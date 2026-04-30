import re
from typing import Optional

from pydantic import BaseModel, field_validator


class ProductCreateSchema(BaseModel):
    barcode: str
    name: str

    @field_validator("barcode")
    def validate_barcode(cls, v):
        v = v.strip().replace(" ", "")

        if not re.fullmatch(r"\d{8}|\d{12,14}", v):
            raise ValueError("Invalid barcode format")

        return v


class OpenBeautyFactsProduct(BaseModel):
    """Pydantic-схема API openbeautyfacts
    Без Optional будет падать, т.к. API может не вернуть поле, может вернуть null, может вернуть пустую строку
    """

    product_name: Optional[str] = None
    brands: Optional[str] = None
    categories: Optional[str] = None
    ingredients_text_en: Optional[str] = None
    image_front_url: Optional[str] = None
    packaging: Optional[str] = None
    quantity: Optional[str] = None
    countries: Optional[str] = None


class OpenBeautyFactsResponse(BaseModel):
    status: int
    product: Optional[OpenBeautyFactsProduct] = None

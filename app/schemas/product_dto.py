from typing import Optional

from pydantic import BaseModel, Field


class AdditionalInfo(BaseModel):
    packaging: Optional[str] = Field(default=None, alias="Упаковка")
    weight: Optional[str] = Field(default=None, alias="Вес")
    country: Optional[str] = Field(default=None, alias="Страна")


class ProductDTO(BaseModel):
    barcode: str
    name: str
    brand: str
    category: str
    ingredients: str
    image_url: str | None
    additional_info: AdditionalInfo

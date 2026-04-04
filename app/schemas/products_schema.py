from pydantic import BaseModel, field_validator
import re


class ProductCreateSchema(BaseModel):
    barcode: str
    name: str

    @field_validator("barcode")
    def validate_barcode(cls, v):
        v = v.strip().replace(" ", "")

        if not re.fullmatch(r"\d{8}|\d{12,14}", v):
            raise ValueError("Invalid barcode format")

        return v
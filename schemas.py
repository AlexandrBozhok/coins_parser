from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: int
    url: str
    image_url: str
    material: str | None = None
    circulation: int | str | None = None
    year_of_production: int

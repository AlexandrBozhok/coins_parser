import datetime

from pydantic import BaseModel, validator


class Product(BaseModel):
    created: datetime.datetime = None
    updated: datetime.datetime = None
    name: str
    price: int
    url: str
    image_url: str
    material: str | None = None
    circulation: int | str | None = None
    year_of_production: int
    sold_out: bool = False

    @validator('created', pre=True, always=True)
    def set_created(cls, v):
        return v or datetime.datetime.now()

    @validator('updated', pre=True, always=True)
    def set_updated(cls, v):
        return v or datetime.datetime.now()

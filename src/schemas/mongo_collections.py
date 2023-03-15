import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, validator, Field
from pydantic.types import PositiveInt


class Product(BaseModel):
    created: datetime.datetime = None
    available_from: datetime.datetime = None
    updated: datetime.datetime = None
    bank_product_id: int
    name: str
    price: int
    url: str
    image_url: str
    material: str | None = None
    circulation: int | str | None = None
    year_of_production: int | None = None
    sold_out: bool = False

    @validator('created', 'available_from', 'updated', pre=True, always=True)
    def set_dates(cls, v):
        return v or datetime.datetime.now()


class ProductUpdateFields(BaseModel):
    available_from: datetime.datetime | None = None
    updated: datetime.datetime | None = None
    price: PositiveInt | None = None
    sold_out: bool | None = None


class Payment(BaseModel):
    id: Any = Field(alias='_id')
    client_id: str
    created: datetime.datetime | None = None
    updated: datetime.datetime | None = None
    amount: PositiveInt
    status: str = 'NEW_INVOICE'  # Enum need
    invoice_url: str
    is_expired: bool = False

    class Config:
        allow_population_by_field_name = True

    @validator('created', 'updated', pre=True, always=True)
    def set_dates(cls, v):
        return v or datetime.datetime.now()

    @validator('id', pre=True, always=True)
    def set_id(cls, v):
        if isinstance(v, ObjectId):
            return v
        return ObjectId(v)


class PaymentUpdateFields(BaseModel):
    updated: datetime.datetime | None = None
    status: str | None = None
    is_expired: bool | None = None

    @validator('updated', pre=True, always=True)
    def set_updated(cls, v):
        return v or datetime.datetime.now()


class PaymentIn(BaseModel):
    id: Any = Field(alias='_id')
    client_id: str
    amount: PositiveInt
    invoice_url: str

    class Config:
        allow_population_by_field_name = True

    @validator('id', pre=True, always=True)
    def set_id(cls, v):
        if isinstance(v, ObjectId):
            return v
        return ObjectId(v)


class Client(BaseModel):
    created: datetime.datetime
    updated: datetime.datetime
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    chat_id: int
    expired_at: datetime.datetime | None
    in_channel: bool


class ClientUpdateFields(BaseModel):
    expired_at: datetime.datetime | None = None
    in_channel: bool | None = None


class ClientIn(BaseModel):
    created: datetime.datetime | None = None
    updated: datetime.datetime | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    chat_id: int
    expired_at: datetime.datetime | None = None
    in_channel: bool = False

    @validator('created', 'updated', 'expired_at', pre=True, always=True)
    def set_dates(cls, v):
        return v or datetime.datetime.now()


class ClientOut(BaseModel):
    id: str = Field(alias='_id')
    created: datetime.datetime
    updated: datetime.datetime
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    chat_id: int
    payments: list[Payment] = []
    expired_at: datetime.datetime | None = None
    in_channel: bool

    @validator('id', pre=True, always=True)
    def set_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class Invite(BaseModel):
    created: datetime.datetime | None = None
    link: str
    expired_at: datetime.datetime

    @validator('created', pre=True, always=True)
    def set_dates(cls, v):
        return v or datetime.datetime.now()

import datetime

from pydantic import BaseModel, validator, PositiveInt, PositiveFloat
from pydantic.utils import to_lower_camel


class PaymentSignParams(BaseModel):
    merchant_account: str
    merchant_domain_name: str
    order_reference: str
    order_date: PositiveInt
    amount: PositiveInt
    currency: str
    product_name: str
    product_count: PositiveInt
    product_price: PositiveInt

    @validator('product_name', 'product_price', 'product_count', pre=True, always=True)
    def get_from_list(cls, v):
        if isinstance(v, list):
            return v[0]
        return v


class PaymentInvoiceParams(BaseModel):
    transaction_type: str = 'CREATE_INVOICE'
    merchant_account: str
    merchant_domain_name: str
    merchant_signature: str | None = None
    api_version: int = 1
    language: str = "UA"
    service_url: str | None = None
    order_reference: PositiveInt | str
    order_date: PositiveInt
    amount: PositiveFloat
    currency: str
    order_timeout: PositiveInt
    product_name: list[str]
    product_price: list[PositiveInt]
    product_count: list[PositiveInt]

    @validator('product_name', 'product_price', 'product_count', pre=True, always=True)
    def put_in_list(cls, v):
        if isinstance(v, list):
            return v
        return [v]

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_lower_camel


class PaymentApproveParams(BaseModel):
    order_reference: str
    status: str
    time: int | None = None

    @validator('time', pre=True, always=True)
    def set_time(cls, v):
        return v or int(datetime.datetime.now().timestamp())

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_lower_camel


class ServerApproveResponse(BaseModel):
    order_reference: str
    status: str
    time: int | None = None
    signature: str

    @validator('time', pre=True, always=True)
    def set_time(cls, v):
        return v or int(datetime.datetime.now().timestamp())

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_lower_camel


class FondyPaymentParams(BaseModel):
    order_id: str
    currency: str = 'UAH'
    amount: int
    lang: str = 'uk'
    lifetime: int = 36000

    @validator('amount')
    def set_amount(cls, v):
        return v * 100  # Переводимо суму в копійки

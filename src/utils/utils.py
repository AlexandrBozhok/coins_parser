import datetime

from src.config.settings import settings
from src.schemas.payment import PaymentSignParams


def generate_payment_sign_params(order_reference: str):
    return PaymentSignParams(
        merchant_account=settings.merchant_account,
        merchant_domain_name=settings.merchant_domain_name,
        order_reference=order_reference,
        order_date=int(datetime.datetime.now().timestamp()),
        amount=settings.service_price,
        currency='UAH',
        product_name=settings.service_name,
        product_count=1,
        product_price=settings.service_price
    )

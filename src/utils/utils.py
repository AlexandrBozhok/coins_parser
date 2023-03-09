import datetime

from src.config.settings import settings
from src.schemas.payment import PaymentSignParams


def generate_payment_sign_params(order_reference: str):
    return PaymentSignParams(
        merchant_account=settings.merchant_account,
        merchant_domain_name=settings.merchant_domain_name,
        order_reference=order_reference,
        order_date=int(datetime.datetime.now().timestamp()),
        amount=1,
        currency='UAH',
        product_name='Підписка на оновлення інтернет магазину',
        product_count=1,
        product_price=1
    )

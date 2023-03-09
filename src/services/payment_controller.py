import datetime
import hmac
import logging
from typing import Any

import requests

from src.config.settings import settings
from src.schemas.payment import PaymentSignParams, PaymentInvoiceParams, PaymentApproveParams, ServerApproveResponse


class PaymentController:
    order_timeout = 3600  # in seconds

    @classmethod
    def _create_signature(cls, secret_key: str, sign_values: list[Any]) -> str:
        sign = ';'.join([str(item) for item in sign_values])
        print(sign)
        return hmac.new(secret_key.encode('utf-8'), sign.encode('utf-8'), 'MD5').hexdigest()

    @classmethod
    def _get_invoice_url(cls, invoice_params: PaymentInvoiceParams) -> str | None:
        response = requests.post(
            url=settings.way_for_pay_api_url,
            json=invoice_params.dict(by_alias=True)
        ).json()
        # OK:
        # {'invoiceUrl': 'Some url', 'reason': 'Ok', 'reasonCode': 1100, 'qrCode': 'Some url'}

        # Not OK:
        # {'reasonCode': 1109, 'reason': 'Message Error'}
        # {'invoiceUrl': None, 'reason': 'Duplicate Order ID', 'reasonCode': 1112}
        if 'invoiceUrl' in response:
            logging.info(f'New payment url: {response["invoiceUrl"]}')
            return response['invoiceUrl']
        logging.error(f'Error on getting invoiceUrl from provider. Message: {response["reason"]}')
        return

    @classmethod
    def create_invoice_url(cls, sign_params: PaymentSignParams) -> str | None:
        signature = cls._create_signature(
            secret_key=settings.owner_secret_key,
            sign_values=[item for item in sign_params.dict().values()]
        )

        payment_invoice_params = PaymentInvoiceParams(
            order_timeout=cls.order_timeout,
            service_url=settings.service_url,
            merchant_signature=signature,
            **sign_params.dict()
        )

        invoice_url = cls._get_invoice_url(payment_invoice_params)
        return invoice_url

    @classmethod
    def create_approve_response(cls, params: dict[str, Any]) -> dict:
        payment_approve_params = PaymentApproveParams(status='accept', **params)
        signature = cls._create_signature(
            secret_key=settings.owner_secret_key,
            sign_values=[item for item in payment_approve_params.dict().values()]
        )
        approve_response = ServerApproveResponse(
            order_reference=payment_approve_params.order_reference,
            status='accept',
            signature=signature
        )
        return approve_response.dict(by_alias=True)

from typing import Any

from bson import ObjectId

from models.collections import PaymentsCollection
from src.schemas.mongo_collections import Payment, PaymentIn, PaymentUpdateFields


class PaymentCRUD:

    @classmethod
    async def get_one(cls, payment_id: str) -> dict[str, Any] | None:
        product = await PaymentsCollection.find_one({"_id": ObjectId(payment_id)})
        if product:
            return product
        return

    @classmethod
    async def insert_one(cls, payment_in: PaymentIn):
        payment = Payment(**payment_in.dict(exclude_none=True, by_alias=True))
        result = await PaymentsCollection.insert_one(payment.dict(by_alias=True))
        return result.inserted_id

    @classmethod
    async def update_one(cls, payment_id: str, update_fields: PaymentUpdateFields):
        result = await PaymentsCollection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': update_fields.dict(exclude_none=True)}
        )
        return result

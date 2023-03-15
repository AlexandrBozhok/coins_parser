from typing import Any

from bson import ObjectId

from src.models.collections import CoinsCollection
from src.schemas.mongo_collections import Product, ProductUpdateFields


class ProductCRUD:

    @classmethod
    async def get_one(cls, product_id: str) -> dict[str, Any] | None:
        product = await CoinsCollection.find_one({"_id": ObjectId(product_id)})
        if product:
            return product
        return

    @classmethod
    async def get_many(cls,
                       filter: dict[str, Any] | None = None,
                       need_fields: dict[str, Any] | None = None,
                       return_cursor: bool = False):
        cursor = CoinsCollection.find(filter, need_fields)
        if return_cursor:
            return cursor
        return [item async for item in cursor]

    @classmethod
    async def insert_many(cls, products: list[Product]) -> str | None:
        result = await CoinsCollection.insert_many([item.dict() for item in products])
        return result.inserted_ids

    @classmethod
    async def update_one(cls, product_id: str, update_fields: ProductUpdateFields):
        result = await CoinsCollection.update_one(
            {'_id': product_id},
            {'$set': update_fields.dict(exclude_none=True)}
        )
        return result

    @classmethod
    async def update_many(cls, filter: dict[str, dict[str, Any]], update_fields: ProductUpdateFields):
        result = await CoinsCollection.update_many(
            filter,
            {'$set': update_fields.dict(exclude_none=True)}
        )
        return result

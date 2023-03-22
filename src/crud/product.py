from typing import Any

from bson import ObjectId

from src.models.collections import CoinsCollection
from src.schemas.mongo_collections import Product, ProductUpdateFields, ProductOut


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
        return [ProductOut(**item) async for item in cursor]

    @classmethod
    async def insert_one(cls, product: Product) -> str | None:
        result = await CoinsCollection.insert_one(product.dict())
        return result.inserted_id

    @classmethod
    async def insert_many(cls, products: list[Product]) -> str | None:
        result = await CoinsCollection.insert_many([item.dict() for item in products])
        return result.inserted_ids

    @classmethod
    async def update_one(cls,
                         update_fields: ProductUpdateFields,
                         product_id: str | None = None,
                         bank_product_id: int | None = None):
        if not product_id and not bank_product_id:
            raise AttributeError(f'product_id and bank_product_id is empty. Need one field for filter')
        filter = {'_id': product_id} if product_id else {'bank_product_id': bank_product_id}
        result = await CoinsCollection.update_one(
            filter,
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

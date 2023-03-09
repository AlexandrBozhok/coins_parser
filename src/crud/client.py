from typing import Any

from bson import ObjectId

from src.models.collections import ClientsCollection, PaymentsCollection
from src.schemas.mongo_collections import Client, ClientIn, ClientOut, ClientUpdateFields


class ClientCRUD:

    @classmethod
    async def get_one(cls, id: str | None = None, chat_id: int | None = None):
        if id:
            filter = {'_id': ObjectId(id)}
        elif chat_id:
            filter = {'chat_id': chat_id}
        else:
            return

        result = await ClientsCollection.find_one(filter)
        if result:
            payments_cursor = PaymentsCollection.find({'client_id': result['_id']})
            result['payments'] = [item async for item in payments_cursor]
            return ClientOut(**result)
        return

    @classmethod
    async def get_many(cls, filter: dict[str, Any], with_payments=False):
        cursor = ClientsCollection.find(filter)
        if with_payments:
            clients = []
            async for item in cursor:
                payments_cursor = PaymentsCollection.find({'client_id': item['_id']})
                item['payments'] = [item async for item in payments_cursor]
                clients.append(ClientOut(**item))
            return clients
        return [ClientOut(**item) async for item in cursor]

    @classmethod
    async def insert_one(cls, client_in: ClientIn):
        client = Client(**client_in.dict())
        result = await ClientsCollection.insert_one(client.dict())
        return result.inserted_id

    @classmethod
    async def update_one(cls, client_id: str, update_fields: ClientUpdateFields):
        result = await ClientsCollection.update_one(
            {'_id': ObjectId(client_id)},
            {'$set': update_fields.dict(exclude_none=True)}
        )
        return result

    @classmethod
    async def exists_by_chat_id(cls, chat_id: int) -> bool:
        result = await ClientsCollection.find_one({"chat_id": chat_id})
        return bool(result)

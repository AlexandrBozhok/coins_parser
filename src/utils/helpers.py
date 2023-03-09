import datetime

from monthdelta import monthdelta

from src.crud.client import ClientCRUD
from src.schemas.mongo_collections import ClientUpdateFields, ClientOut
from src.utils.enums import ExpireDateAction


async def update_client_expire_date(client_id: str, action: ExpireDateAction):
    client = await ClientCRUD.get_one(id=client_id)
    if client:
        print(client)
        if action == 'add':
            new_expire_date = client.expired_at + monthdelta(1)
        else:
            new_expire_date = client.expired_at - monthdelta(1)

        result = await ClientCRUD.update_one(client_id, ClientUpdateFields(expired_at=new_expire_date))
        print(result.modified_count)


def client_has_active_sub(client: ClientOut):
    # Return True if subscribe is active
    return client.expired_at.timestamp() > datetime.datetime.now().timestamp()

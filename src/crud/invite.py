from typing import Any

from models.collections import InviteCollection
from src.schemas.mongo_collections import Invite


class InviteCRUD:

    @classmethod
    async def get(cls) -> dict[str, Any] | None:
        link = await InviteCollection.find_one({})
        if link:
            return link
        return

    @classmethod
    async def update_or_create(cls, invite: Invite):
        result = await InviteCollection.update_one({}, {'$set': invite.dict()}, upsert=True)
        return result

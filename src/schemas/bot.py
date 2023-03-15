from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel


class MessageKeyboard(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_keyboard

    @classmethod
    def validate_keyboard(cls, keyboard):
        if isinstance(keyboard, InlineKeyboardMarkup):
            return keyboard
        raise ValueError(f'Invalid field: keyboard')


class MessageModel(BaseModel):
    text: str
    keyboard: MessageKeyboard | None = None

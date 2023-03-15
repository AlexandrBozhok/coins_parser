import motor.motor_asyncio

from aiogram import Bot, Dispatcher

from src.config.settings import settings


mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url(), serverSelectionTimeoutMS=5000)

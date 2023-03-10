import logging
from logging.config import dictConfig

from pydantic import BaseSettings, BaseModel


class Settings(BaseSettings):
    nbu_shop_base_url: str

    # Telegram Bot
    bot_api_token: str
    webhook_base_url: str
    channel_id: str

    # MongoDB
    db_host: str
    db_collection: str
    db_user: str
    db_password: str

    # WayForPay
    way_for_pay_api_url: str
    owner_secret_key: str
    merchant_account: str
    merchant_domain_name: str
    service_url: str

    # Service
    service_name: str
    service_price: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def mongodb_url(self) -> str:
        return f'mongodb+srv://{self.db_user}:{self.db_password}@{self.db_host}/?retryWrites=true&w=majority'

    def bot_webhook(self) -> str:
        return f'{self.webhook_base_url}/bot/{self.bot_api_token}'


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "coin_parser"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


settings = Settings()
dictConfig(LogConfig().dict())
logger = logging.getLogger("coin_parser")

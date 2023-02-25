from pydantic import BaseSettings


class Settings(BaseSettings):
    nbu_shop_base_url: str

    # Telegram Bot
    bot_api_token: str
    chat_id: str

    # MongoDB
    db_host: str
    db_user: str
    db_password: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

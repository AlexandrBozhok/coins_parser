from pydantic import BaseSettings


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


settings = Settings()

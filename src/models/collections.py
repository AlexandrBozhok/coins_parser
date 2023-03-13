from motor.core import AgnosticCollection, AgnosticDatabase

from src.config.settings import settings
from src.initializer import mongo_client


# Databases
db_name = 'dev_coins_db' if settings.develop else 'coins-db'
CoinsDB: AgnosticDatabase = mongo_client[db_name]


# Collections

CoinsCollection: AgnosticCollection = CoinsDB['coins']
ClientsCollection: AgnosticCollection = CoinsDB['clients']
PaymentsCollection: AgnosticCollection = CoinsDB['payments']
InviteCollection: AgnosticCollection = CoinsDB['invites']

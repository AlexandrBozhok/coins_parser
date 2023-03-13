from motor.core import AgnosticCollection, AgnosticDatabase

from src.config.settings import settings
from src.initializer import mongo_client


# Databases
db_name = 'coins-db' if settings.develop else 'dev_coins_db'
CoinsDB: AgnosticDatabase = mongo_client[db_name]


# Collections

CoinsCollection: AgnosticCollection = CoinsDB['coins']
ClientsCollection: AgnosticCollection = CoinsDB['clients']
PaymentsCollection: AgnosticCollection = CoinsDB['payments']
InviteCollection: AgnosticCollection = CoinsDB['invites']

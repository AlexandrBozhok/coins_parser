from motor.core import AgnosticCollection, AgnosticDatabase

from config.settings import settings
from initializer import mongo_client


# Databases

CoinsDB: AgnosticDatabase = mongo_client['dev_coins_db']


# Collections

CoinsCollection: AgnosticCollection = CoinsDB['coins']
ClientsCollection: AgnosticCollection = CoinsDB['clients']
PaymentsCollection: AgnosticCollection = CoinsDB['payments']
InviteCollection: AgnosticCollection = CoinsDB['invites']

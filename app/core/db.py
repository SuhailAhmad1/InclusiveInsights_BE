from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import DB_URI
import logging

# Suppress PyMongo logs
logging.getLogger("pymongo").setLevel(logging.ERROR)

uri = DB_URI

client = MongoClient(uri, server_api=ServerApi('1'))

db = client["InclusiveInsights"]

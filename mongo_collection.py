import os
import sys
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

mongo_host = os.getenv("MONGO_HOST")
mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_db_name = os.getenv("MONGO_DATABASE_NAME")
mongo_collection_name = os.getenv("MONGO_COLLECTION_NAME")


def get_db_collection():
    client = MongoClient(mongo_host, username=mongo_user, password=mongo_password)
    check_mongo_connection(client)
    db = client[mongo_db_name]
    return db[mongo_collection_name]


def check_mongo_connection(client):
    try:
        client.server_info()
    except ServerSelectionTimeoutError:
        sys.exit("MongoDB timed out")

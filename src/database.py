import os

from src.config import Config
from pymongo import MongoClient

# Schema for user
user_schema = {
    'user_id': str,
    'credentials': str
}

# Define the mongo client and db details
client = MongoClient(Config.MONGO_URL)
db = client[Config.MONGO_DB]
collection = db[Config.MONGO_COLLECTION]

class MongoDBError(Exception):
    pass

def add_user_db(user_id, credentials):
    try:
        collection.update_one(
            { 'user_id': user_id},
            [ 
                { "$set": { 'credentials': credentials.to_json()} }
            ],
            upsert = True,
        )

    except Exception as e:
        raise MongoDBError(f"Error while adding user to MongoDB: {e}")


def get_user_credentials_db(user_id):
    try:
        user = collection.find_one({'user_id': user_id})
        if user and 'credentials' in user:
           return user['credentials']
        else:
            raise MongoDBError(f"User not found in the database")
    except Exception as e:
        raise MongoDBError(f"Error while getting user credentials from MongoDB: {e}")
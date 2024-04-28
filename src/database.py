import os
import json

from src.config import Config
from pymongo import MongoClient
import google.oauth2.credentials

# Schema for user
user_schema = {
    'user_id': str,
    'credentials': str,
    'credentials_data': dict
}

# Define the mongo client and db details
client = MongoClient(Config.MONGO_URL)
db = client[Config.MONGO_DB]
collection = db[Config.MONGO_COLLECTION]

class MongoDBError(Exception):
    pass

def add_user_db(user_id, credentials):
    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.isoformat(),
    }
    try:
        collection.update_one(
            {'user_id': user_id},
            {'$set': {
                'credentials_data': credentials_data,
                'credentials': credentials.to_json()
            }},
            upsert=True
        )
    except Exception as e:
        raise MongoDBError(f"Error while adding user to MongoDB: {e}")


def get_user_credentials_db(user_id):
    try:
        user = collection.find_one({'user_id': user_id})
        if user and 'credentials' in user:
            credentials_info = json.loads(user['credentials'])
            credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(credentials_info)
            return credentials
        else:
            raise MongoDBError(f"User with ID {user_id} not found in the database")
    except Exception as e:
        raise MongoDBError(f"Error while getting user credentials from MongoDB: {e}")
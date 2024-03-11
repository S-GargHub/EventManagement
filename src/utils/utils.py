from datetime import datetime
from src.database import add_user_db, get_user_credentials_db


def getUserCredentials(user_id):
    try:
        credentials = get_user_credentials_db(user_id)
        if not credentials.valid:
            try:
                #credentials = get creds from user
                add_user_db(user_id, credentials)
            except Exception as e:
                print(f"Error occured: {e}")
                return 
    except Exception as e:
        print(f"Error occured: {e}")
        return
    return credentials
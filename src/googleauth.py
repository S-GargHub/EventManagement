import os
import json
import datetime
import google.auth.exceptions

from src.config import Config
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_CLIENT_CONFIG = json.loads(Config.GOOGLE_CLIENT_JSON)
SCOPES = Config["GOOGLE_AUTH_SCOPE"]

def getCredentials():
    credentials = None
    try:
        if os.path.exists("token.json"):
            credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        GOOGLE_CLIENT_CONFIG, SCOPES
                    )
                    credentials = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(credentials.to_json())
    except Exception as e:
        raise Exception(f"Error occured: {e}")
    return credentials
import os
import json
import datetime
import requests
import google.auth.exceptions

from src.config import Config
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_CLIENT_CONFIG = Config.GOOGLE_CLIENT_JSON
SCOPES = Config.GOOGLE_AUTH_SCOPE


def get_user_info(credentials):
    token_request = Request(session=requests.session())
    try:
        info = id_token.verify_oauth2_token(id_token=credentials.id_token, request=token_request, audience=GOOGLE_CLIENT_ID)
        return info
    except Exception as e:
        raise Exception(f"Error occured: {e}")

def getCredentials():
    credentials = None
    try:
        if os.path.exists("token.json"):
            credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_CONFIG, SCOPES)
                    credentials = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(credentials.to_json())
    except Exception as e:
        raise Exception(f"Error occured: {e}")
    return credentials


def get_flow():
    return 
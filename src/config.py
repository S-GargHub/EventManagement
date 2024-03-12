import os
from dotenv import load_dotenv

class Config:
    load_dotenv(os.path.join("../", '.env'))
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_JSON = os.environ.get('GOOGLE_CLIENT_JSON')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    GOOGLE_AUTH_SCOPE=[
            #https://developers.google.com/identity/protocols/oauth2/scopes#oauth2
            "https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid",
            
            #https://developers.google.com/identity/protocols/oauth2/scopes#calendar
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
            ]


    MONGO_URL = os.environ.get('MONGO_URL')
    MONGO_DB = os.environ.get('MONGO_DB')
    MONGO_COLLECTION = os.environ.get('MONGO_COLLECTION')

    REDIRECT_URI =  os.environ.get("REDIRECT_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY")
import os
import requests
import subprocess
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
    
    #REDIRECT_URI = os.environ.get("REDIRECT_URI")
    try:
        response = requests.put('http://169.254.169.254/latest/api/token', headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'})
        response.raise_for_status()  # Raise an exception for non-2xx responses
        access_token = response.text.strip()

        response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', headers={'X-aws-ec2-metadata-token': access_token})
        if response.status_code == 200:
            public_ip = response.text.strip()
            REDIRECT_URI = f"https://{public_ip}.nip.io:5000/oauth2callback"
        else:
            print("Failed to retrieve public IP from instance metadata, redirecting to localhost", response.text)
            REDIRECT_URI = os.environ.get("REDIRECT_URI")
    except requests.RequestException as e:
        print("Error retrieving public IP from instance metadata:", e)
        REDIRECT_URI = os.environ.get("REDIRECT_URI")

    print(REDIRECT_URI)
    SECRET_KEY = os.environ.get("SECRET_KEY")
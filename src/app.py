import os

from src.config import Config
from src.googleauth import get_user_info
from google_auth_oauthlib.flow import InstalledAppFlow
from src.database import add_user_db, get_user_credentials_db
from flask import Flask, request, redirect, session, render_template, abort


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_CONFIG = Config.GOOGLE_CLIENT_JSON
SCOPES = Config.GOOGLE_AUTH_SCOPE

app = Flask(__name__)
app.config.from_object(Config)
flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_CONFIG, SCOPES)
flow.redirect_uri = Config.REDIRECT_URI
    
@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/login")
def login():
    try:
        #autorize the user after fetching the details and set the session
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', select_accoun='true')
        session["state"] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"Error occured while logging in {e}")
        return redirect("/")
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route("/oauth2callback")
def oauth2callback():
    try:
        flow.fetch_token(authorization_response=request.url)
        if not session["state"] == request.args["state"]: #state is not matching
            abort(500)
        credentials = flow.credentials
        user_info = get_user_info(credentials)
        session['user_id'] = user_info['sub']
        session['name'] = user_info['name']

        user_id = user_info['sub']
        add_user_db(user_id=user_id, credentials=credentials)
        return redirect("/events")
    except Exception as e:
        print(f"Error occured: {e}")
        return redirect("/")

@app.route("/events", methods=["GET"])
def get_events():
    return render_template("events.html")
    



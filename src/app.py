import os

from src.config import Config
from src.googleauth import get_user_info
from google_auth_oauthlib.flow import InstalledAppFlow
from src.database import add_user_db, get_user_credentials_db
from flask import Flask, request, redirect, session, render_template, abort, url_for
from src.utils.utils import validate_dates, user_id_is_required, get_user_credentials
from src.calender import get_calender_events, get_upcoming_calender_events

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
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', select_account='true', approval_prompt='force')
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
        return redirect("/menu")
    except Exception as e:
        print(f"Error occured: {e}")
        return redirect("/")

@app.route("/menu", methods=["GET"])
def get_menu():
    return render_template("menu.html")

@app.route("/rangeEvents", methods=["GET"])
def get_range():
    return render_template("rangeEvents.html")

@app.route("/rangeEvents", methods=["POST"])
@user_id_is_required
@validate_dates
@get_user_credentials
def post_events(user_id, dates, credentials):
    start_date, end_date = dates

    try:
        event_list = get_calender_events(credentials, start_date, end_date)
        return render_template('display.html', start_date=start_date, end_date=end_date, event_list=event_list)
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")
    
# @app.route("/upcomingEvents", methods=["POST"])
# @user_id_is_required
# @validate_dates
# @get_user_credentials
# def post_events(user_id, dates, credentials):
#     start_date, end_date = dates
#     try:
#         event_list = get_upcoming_calender_events(credentials)
#         return render_template('display.html', start_date=start_date, end_date=end_date, event_list=event_list)
#     except Exception as error:
#         print(f"Error occured: {error}")
#         return redirect("/")
    

    
    



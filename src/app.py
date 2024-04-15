import os


from src.config import Config
from src.googleauth import get_user_info
from datetime import datetime, timezone, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from src.database import add_user_db, get_user_credentials_db
from flask import Flask, request, redirect, session, render_template, abort, url_for, jsonify
from src.utils.utils import validate_dates, user_id_is_required, get_user_credentials
from src.calendarAccess import get_events, create_event, delete_event, EventNotFoundException

from src.awsBackend import put_event_metadata_dynamodb, delete_event_dynamodb

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
        event_list = get_events(credentials, start_date, end_date)
        return render_template('display.html', start_date=start_date, end_date=end_date, event_list=event_list)
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")
    
@app.route("/upcomingEvents", methods=["GET"])
@user_id_is_required
@get_user_credentials
def get_calender_events(user_id, credentials):
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        event_list = get_events(credentials, start_date, end_date)
        return render_template('display.html', start_date=start_date, end_date=end_date, event_list=event_list)
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")
    

@app.route("/createEvent", methods=["GET"])
def get_event_details():
    return render_template("createEvent.html")

@app.route("/createEvent", methods=["POST"])
@user_id_is_required
@get_user_credentials
def create_calendar_event(user_id, credentials):
    summary = request.form['event-summary']
    start_date = datetime.fromisoformat(request.form['start-date'])
    end_date = datetime.fromisoformat(request.form['end-date'])
    participants = request.form.getlist('participants[]')  # Get the list of participants
    # print(participants)
    try:
        event = create_event(credentials, summary, start_date, end_date, participants)
        
        # Insert event metadata into DynamoDB
        put_event_metadata_dynamodb(event, summary, start_date, end_date) ## add participant later

        return render_template('eventDetails.html', start_date=start_date, end_date=end_date, summary=summary, event_link=event.get("htmlLink"))
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")
    
@app.route("/deleteEvent", methods=["GET", "POST"])
@user_id_is_required
@get_user_credentials
def delete_calendar_event(user_id, credentials):
    if request.method == "GET":
        return render_template("deleteEvent.html")
    else:
        event_id = request.form['event-id']
        try:
            deleted = delete_event(credentials, event_id)

            delete_event_dynamodb(event_id)
            ## also write the lambda function to see if the item was deleted

            return jsonify({'message': 'Event deleted successfully', 'id':deleted['id'], 'time':deleted['time'], 'summary':deleted['summary']})
            #return redirect("https://calendar.google.com/calendar/render")
        except EventNotFoundException as error:
            return jsonify({'error': (error.message)}), 500
            return redirect("/")
        except Exception as error:
            print(f"Error occured: {error}")
            return jsonify({'error': (error.message)}), 500
            return redirect("/")

    
    

###---------------- AWS Stuff ----------------------------------------------------------------
@app.route("/awsFeatures", methods=["GET"])
def get_AWS_menu():
    return render_template("awsFeatures.html")
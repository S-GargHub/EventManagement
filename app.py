import os
import json
import boto3

from src.config import Config
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import Flask, request, redirect, session, render_template, abort, jsonify, flash, url_for

from src.database import add_user_db
from src.googleauth import get_user_info
from src.utils.utils import validate_dates, user_id_is_required, get_user_credentials
from src.calendarAPI import get_events, create_event, delete_event, EventNotFoundException

from src.awsBackend import put_event_metadata_dynamodb, delete_event_dynamodb, find_event_s3, upload_file_S3, get_s3_content


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config.from_object(Config)

flow = InstalledAppFlow.from_client_secrets_file(Config.GOOGLE_CLIENT_JSON, Config.GOOGLE_AUTH_SCOPE)
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
        event_list = get_events(credentials.to_json(), start_date, end_date)
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
         # Invoke the Lambda function
        lambda_client = boto3.client('lambda')
        payload = {
            'user_id': user_id,
            'credentials': credentials.to_json()
        }

        response = lambda_client.invoke(
            FunctionName='myLambda',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        if response['StatusCode'] == 200:
            event_list = json.loads(response['Payload'].read().decode())
        else:
            print(f"FunctionError: {response['FunctionError']}")

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


###---------------- AWS Endpoints----------------------------------------------------------------
@app.route("/homeworkSubmission", methods=["GET", "POST"])
@user_id_is_required
@get_user_credentials
def get_homeworkSubmission(user_id, credentials):
    if request.method == "GET":
        return render_template("/homeworkSubmission.html")
    else:
        event_id = request.form['event-id']

        if find_event_s3(event_id):
            # Folder exists, redirect to uploadHomework.html
            return redirect(url_for('uploadingHomework', event_id=event_id))
        else:
            # Folder doesn't exist, show an error prompt
            return render_template("/homeworkSubmission.html", message="Invalid Event ID!")



@app.route("/uploadHomework", methods=["GET", "POST"])
@user_id_is_required
@get_user_credentials
def uploadingHomework(user_id, credentials):
    event_id = session.get('event_id')
    if not event_id:
        return redirect("/menu")
    if request.method == "GET":
        event_id = request.args.get('event_id')
        session['event_id'] = event_id  # Store the event ID in the session
        return render_template("/uploadHomework.html", event_id=event_id)
    else:
        event_id = request.form.get('event_id')
        # print("event_id:", event_id)
        file = request.files.get('file')

        # Upload the file to S3 in the event_id folder
        try:
            upload_file_S3(file, event_id)
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return render_template("/uploadHomework.html", message="Failed! Try again.")
        
        return render_template("/uploadHomework.html", event_id=event_id, message="File Uploaded Successfully!")


@app.route("/dashboard", methods=["GET"])
@user_id_is_required
@get_user_credentials
def dashboard(user_id, credentials):
    event_id = session.get('event_id')
    if not event_id:
        return redirect("/menu")
    if request.method == "GET":
        # print("Dashboard: ", event_id)
        s3_content = get_s3_content(event_id)
        return render_template("/dashboard.html", event_id=event_id, s3_content=s3_content)


if __name__ == "__main__":
    # Run the Flask application with host='0.0.0.0' to listen on all network interfaces
    app.run(host='0.0.0.0')
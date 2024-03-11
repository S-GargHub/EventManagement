from flask import Flask, request, redirect, session, render_template
from src.utils.utils import get_user_credentials_db
from src.database import add_user_db, get_user_credentials_db
from src.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/login")
def login():
    try:
        #autorize the user after fetting the details and set the session
        session['state']
        return redirect()
    except Exception as e:
        print(f"Error occured while logging in {e}")
        return redirect("/")
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# temporarily adding - then will use secret key when ready to use sessions and login
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ekprayas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/" , methods=["GET", "POST"])
def index():
   return render_template("index.html")


@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    if request.method == "POST":
       ...
    else:
       rows = db.session.execute(text("SELECT * FROM gallery")).fetchall()
       modified_rows = [dict(row._mapping) for row in rows]


@app.route("/about")
def about():
   return render_template("about.html")


@app.route("/blind" , methods=["GET", "POST"])
def blind():
   if request.method == "POST":
      ...

   else:
      return render_template("blind.html")

   


@app.route("/book" , methods=["GET", "POST"])
def book():
   return render_template("book.html")


@app.route("/team" , methods=["GET", "POST"])
def team():
   return render_template("team.html")


@app.route("/initiative")
def initiative():
   return render_template("initiative.html")






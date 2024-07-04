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
      first_name = request.form.get("first_name")
      last_name = request.form.get("last_name")
      gender = request.form.get("inlineRadioOptions")
      email = request.form.get("email")
      mobile_number = request.form.get("mobile_number")
      address = request.form.get("address")
      occupation = request.form.get("occupation")
      occupation_address = request.form.get("occupation_address")
      education = request.form.get("education")
      languages = request.form.getlist("languages")

      photo = request.files.get("photo")
      id_proof = request.files.get("id_proof")

      #TODO: Make the apology function and return the apology template
      if not gender:
         return "gender is required"
      # else:
      #    return f"{gender}"

      if not languages:
         return "Error: At least one language must be selected", 400
      else:
         return jsonify(languages)
         # return f"Languages selected: {', '.join(languages)}"
      # Example for how to add languages in languages column
      # Insert the selected languages into the database
      # cursor.execute("INSERT INTO user_languages (languages) VALUES (?)", (','.join(languages),))
      

   else:
      return render_template("blind.html")

   


@app.route("/book" , methods=["GET", "POST"])
def book():

   if request.method == "POST":
      first_name = request.form.get("first_name")
      last_name = request.form.get("last_name")
      gender = request.form.get("inlineRadioOptions")
      email = request.form.get("email")
      mobile_number = request.form.get("mobile_number")
      address = request.form.get("address")
      occupation = request.form.get("occupation")
      occupation_address = request.form.get("occupation_address")
      education = request.form.get("education")
      languages = request.form.getlist("languages")

      audio = request.files.get("audio")

      #TODO: Make the apology function and return the apology template
      if not gender:
         return "gender is required"
      # else:
      #    return f"{gender}"

      if not languages:
         return "Error: At least one language must be selected", 400
      else:
         return jsonify(languages)
         # return f"Languages selected: {', '.join(languages)}"
      # Example for how to add languages in languages column
      # Insert the selected languages into the database
      # cursor.execute("INSERT INTO user_languages (languages) VALUES (?)", (','.join(languages),))
      

   else:
      return render_template("book.html")


@app.route("/team" , methods=["GET", "POST"])
def team():

   if request.method == "POST":
      first_name = request.form.get("first_name")
      last_name = request.form.get("last_name")
      gender = request.form.get("inlineRadioOptions")
      email = request.form.get("email")
      mobile_number = request.form.get("mobile_number")
      address = request.form.get("address")
      occupation = request.form.get("occupation")
      occupation_address = request.form.get("occupation_address")
      education = request.form.get("education")
      about = request.form.get("about")
      make_change = request.form.get("make_change")
      aadhar_number = request.form.get("aadhar_number")
      pan_number = request.form.get("pan_number")
      aadhar_card = request.form.get("aadhar_card")
      pan_card = request.form.get("pan_card")
      photo = request.files.get("photo")

      #TODO: Make the apology function and return the apology template
      if not gender:
         return "gender is required"
      # else:
      #    return f"{gender}"

   else:
      return render_template("team.html")

   


@app.route("/initiative")
def initiative():
   return render_template("initiative.html")






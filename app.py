import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from helpers import apology

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

      if not first_name:
         return "must provide you first_name"
      
      if not last_name:
         return "must provide last_name"
      
      if not gender:
         return "must provide your gender"
      
      if not email:
         return "must provide email"

      if not mobile_number:
         return "must provide mobile_number"
      
      if not address:
         return "must provide address"

      if not education:
         return "must provide education"
      
      if not languages:
         return "must provide languages"
      
      if not photo:
         return "must provide your photo"
      
      if not id_proof:
         return "must provide your identity proof"

      # Save the file locally
      file_path = os.path.join('uploads', photo.filename)
      photo.save(file_path)

      # Generate the URL
      photo_url = f"/uploads/{photo.filename}"

      file_path = os.path.join('uploads', id_proof.filename)
      id_proof.save(file_path)

      # Generate the URL
      id_proof_url = f"/uploads/{id_proof.filename}"





      #TODO: Make the apology function and return the apology template
      if not gender:
         return "gender is required"
      

      if not languages:
         return "Error: At least one language must be selected", 400
      
      
      try:
         languages_str = ','.join(languages)  # Convert list to comma-separated string

         db.session.execute(
            text(
                  """
                  INSERT INTO blind
                  (first_name, last_name, gender, email, mobile_number, address, occupation, occupation_address, education, languages, photo_url, id_proof_url)
                  VALUES 
                  (:first_name, :last_name, :gender, :email, :mobile_number, :address, :occupation, :occupation_address, :education, :languages, :photo_url, :id_proof_url)
                  """
            ), 
            {
                  "first_name": first_name, 
                  "last_name": last_name, 
                  "gender": gender, 
                  "email": email, 
                  "mobile_number": mobile_number, 
                  "address": address, 
                  "occupation": occupation, 
                  "occupation_address": occupation_address, 
                  "education": education, 
                  "languages": languages_str,  # Use the converted string
                  "photo_url": photo_url, 
                  "id_proof_url": id_proof_url
            }
         )
         db.session.commit()

      except Exception as e:
         db.session.rollback()
         return f"An error occurred: {str(e)}"
   
      flash("Thank You for Submitting Form We Will Get Back to you Soon.")

      return redirect("/blind")

   else:
      return render_template("blind.html")

   


@app.route("/book", methods=["GET", "POST"])
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

        if not first_name:
            flash("Must provide first name", "danger")
            return redirect(url_for("book"))

        if not last_name:
            flash("Must provide last name", "danger")
            return redirect(url_for("book"))

        if not gender:
            flash("Must provide gender", "danger")
            return redirect(url_for("book"))

        if not email:
            flash("Must provide email", "danger")
            return redirect(url_for("book"))

        if not mobile_number:
            flash("Must provide mobile number", "danger")
            return redirect(url_for("book"))

        if not address:
            flash("Must provide address", "danger")
            return redirect(url_for("book"))

        if not education:
            flash("Must provide education", "danger")
            return redirect(url_for("book"))

        if not languages:
            flash("Must provide languages", "danger")
            return redirect(url_for("book"))

        if not audio:
            flash("Must provide your audio file", "danger")
            return redirect(url_for("book"))

        # Check if the file is an audio file
        allowed_audio_types = {'audio/mpeg', 'audio/wav', 'audio/ogg'}
        if audio.mimetype not in allowed_audio_types:
            flash("Invalid audio file type", "danger")
            return redirect(url_for("book"))

        # Ensure upload directory exists
        upload_directory = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)

        # Save the file
        file_path = os.path.join(upload_directory, audio.filename)
        audio.save(file_path)

        # Generate the URL
        audio_url = f"/uploads/{audio.filename}"

        try:
            languages_str = ','.join(languages)  # Convert list to comma-separated string

            db.session.execute(
                text(
                    """
                    INSERT INTO book
                    (first_name, last_name, gender, email, mobile_number, address, occupation, occupation_address, education, languages, audio_url)
                    VALUES 
                    (:first_name, :last_name, :gender, :email, :mobile_number, :address, :occupation, :occupation_address, :education, :languages, :audio_url)
                    """
                ),
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "email": email,
                    "mobile_number": mobile_number,
                    "address": address,
                    "occupation": occupation,
                    "occupation_address": occupation_address,
                    "education": education,
                    "languages": languages_str,  # Use the converted string
                    "audio_url": audio_url
                }
            )
            db.session.commit()
            flash("Form submitted successfully!", "success")
            return redirect(url_for("book"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("book"))

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
      aadhar_card = request.files.get("aadhar_card")
      pan_card = request.files.get("pan_card")
      photo = request.files.get("photo") 


      if not first_name:
         return "must provide you first_name"
      
      if not last_name:
         return "must provide last_name"
      
      if not gender:
         return "must provide your gender"
      
      if not email:
         return "must provide email"

      if not mobile_number:
         return "must provide mobile_number"
      
      if not address:
         return "must provide address"

      if not occupation:
         return "must provide your occupation"
      
      if not occupation_address:
         return "must provide your occupation_address"
      
      if not education:
         return "must provide education"
      
      if not about:
         return "must provide about"
      
      if not make_change:
         return "must provide make_change"
      
      if not aadhar_number:
         return "must provide aadhar_number"
      
      if not pan_number:
         return "must provide pan_number"
      
      if not aadhar_card:
         return "must provide aadhar_card"
      
      if not pan_card:
         return "must provide pan_card"
      
      if not photo:
         return "must provide your photo"
      


      file_path = os.path.join('uploads', aadhar_card.filename)
      aadhar_card.save(file_path)

      # Generate the URL
      aadhar_card_url = f"/uploads/{aadhar_card.filename}"

      file_path = os.path.join('uploads', pan_card.filename)
      pan_card.save(file_path)

      # Generate the URL
      pan_card_url = f"/uploads/{pan_card.filename}"

      file_path = os.path.join('uploads', photo.filename)
      photo.save(file_path)

      # Generate the URL
      photo_url = f"/uploads/{photo.filename}"


      #TODO: Make the apology function and return the apology template
      if not gender:
         return "gender is required"
      # else:
      #    return f"{gender}"


      try:

         db.session.execute(
            text(
                  """
                  INSERT INTO team
                  (first_name, last_name, gender, email, mobile_number, address, occupation, occupation_address, education, about, make_change , aadhar_number ,  pan_number , aadhar_card , pan_card , photo_url)
                  VALUES 
                  (:first_name, :last_name, :gender, :email, :mobile_number, :address, :occupation, :occupation_address, :education, :about, :make_change , :aadhar_number , :pan_number , :aadhar_card , :pan_card , :photo_url)
                  """
            ), 
            {
                  "first_name": first_name,
                  "last_name": last_name,
                  "gender": gender,
                  "email": email,
                  "mobile_number": mobile_number,
                  "address": address,
                  "occupation": occupation,
                  "occupation_address": occupation_address,
                  "education": education,
                  "about": about, 
                  "make_change": make_change,  
                  "aadhar_number": aadhar_number,  
                  "pan_number": pan_number,  
                  "aadhar_card": aadhar_card_url,  
                  "pan_card": pan_card_url, 
                  "photo_url": photo_url  

            }
         )
         db.session.commit()

      except Exception as e:
         db.session.rollback()
         return f"An error occurred: {str(e)}"

   else:
      return render_template("team.html")

   


@app.route("/initiative")
def initiative():
   return render_template("initiative.html")






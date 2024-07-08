import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from helpers import apology

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# temporarily adding - then will use secret key when ready to use sessions and login
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Define the upload folder path within the static folder
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ekprayas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)   

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])




def upload_get_tmp(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file_url = url_for('static', filename=f'uploads/{filename}')
    return file_url



@app.route("/" , methods=["GET", "POST"])
def index():
   return render_template("index.html")


@app.route("/gallery", methods=["GET", "POST"])
def gallery():
   if request.method == "POST":
      action = request.form.get("formToggle")
      event_name = request.form.get("event_name")
      thumbnail = request.files.get("thumbnail")
      files = request.files.getlist('files')

      if not event_name:
         flash("Must provide event name", "danger")
         return redirect(url_for("gallery"))
      
      if not thumbnail:
         flash("Must provide thumbnail", "danger")
         return redirect(url_for("gallery"))
      
      if not files:
         flash("Must provide files", "danger")
         return redirect(url_for("gallery"))
         

      file_urls = []
      for file in files:
         file_url = upload_get_tmp(file)
         file_urls.append(file_url)

      thumbnail_url = upload_get_tmp(thumbnail)

      data = {
        "event_name": event_name,
        "thumbnail_url": thumbnail_url,
        "img1_url": file_urls[0] if len(file_urls) > 0 else None,
        "img2_url": file_urls[1] if len(file_urls) > 1 else None,
        "img3_url": file_urls[2] if len(file_urls) > 2 else None,
        "img4_url": file_urls[3] if len(file_urls) > 3 else None,
        "img5_url": file_urls[4] if len(file_urls) > 4 else None,
        "img6_url": file_urls[5] if len(file_urls) > 5 else None,
        "img7_url": file_urls[6] if len(file_urls) > 6 else None,
        "img8_url": file_urls[7] if len(file_urls) > 7 else None,
        "img9_url": file_urls[8] if len(file_urls) > 8 else None,
        "img10_url": file_urls[9] if len(file_urls) > 9 else None,
        # Add more as needed up to img50_url
      }

      # Prepare your SQL query
      column_names = ', '.join(data.keys())
      placeholders = ', '.join([f':{key}' for key in data.keys()])

      if action == "add":
         query = text(f"""
            INSERT INTO photo_gallery ({column_names})
            VALUES ({placeholders})
         """)

      if action == "edit":
         # Update operation
         event_id = request.form.get("event_id")
         if not event_id:
            flash("Must provide event id", "danger")
            return redirect(url_for("gallery"))
         data["event_id"] = event_id
         query = text(f"""
            UPDATE photo_gallery
            SET {', '.join([f"{key} = :{key}" for key in data.keys() if key != "event_id"])}
            WHERE id = :event_id
         """)

      try:
         db.session.execute(query, data)
         db.session.commit()
      except Exception as e:
         db.session.rollback()
         return f"an error occured {str(e)}"


      flash("Photo Gallery Updated!")
      return redirect("/gallery")

   else:
      rows = db.session.execute(text("SELECT * FROM photo_gallery ORDER BY id DESC")).fetchall()
      modified_rows = [list(row) for row in rows]
      # return jsonify(modified_rows)
      return render_template("gallery.html" , rows = modified_rows)
   


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
         return apology("must provide you first_name", 403)
      
      if not last_name:
         return apology("must provide last_name", 403)
      
      if not gender:
         return apology("must provide your gender", 403)
      
      if not email:
         return apology("must provide email", 403)

      if not mobile_number:
         return apology("must provide mobile_number", 403)
      
      if not address:
         return apology("must provide address", 403)

      if not education:
         return apology("must provide education", 403)
      
      if not languages:
         return apology("must provide languages", 403)
      
      if not photo:
         return apology("must provide your photo", 403)
      
      if not id_proof:
         return apology("must provide your identity proof", 403)

      if len(mobile_number) != 10:
         return apology("Mobile number must be of 10 digits", 403)
      
      # Secure the filename
      photo_filename_secure = secure_filename(photo.filename)

      # Save the file to the upload folder
    #   photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename_secure))

    #   # Construct the full URL for the uploaded file
    #   photo_url = url_for('static', filename=f'uploads/{photo_filename_secure}', _external=True)

    #   id_proof_filename_secure = secure_filename(id_proof.filename)

    #   id_proof.save(os.path.join(app.config['UPLOAD_FOLDER'], id_proof_filename_secure))

    #   id_proof_url = url_for('static', filename=f'uploads/{id_proof_filename_secure}', _external=True)
      photo_url = upload_get_tmp(photo)  
      id_proof_url = upload_get_tmp(id_proof)
      # TODO: Test this code after hosting this online to ensure that the files are stored
      # and also accessible by backend and ngo admin too 
      # TODO: MAKE A FUNCTION TO STORE THESE FILES 
      # TODO: Make a temporary funtion to store all files to test in local machine (as images may not be available through localhost link)
      # TODO: Make a function to store all the files when the site is hosted 
      
      # file_path = os.path.join('uploads', id_proof.filename)
      # id_proof.save(file_path)

      # # Generate the URL
      # id_proof_url = f"/uploads/{id_proof.filename}"





      # #TODO: Make the apology function and return the apology template
      # if not gender:
      #    return "gender is required"
      

      # if not languages:
      #    return "Error: At least one language must be selected", 400
      
      
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
         # return apology("An Error Occured", 500)
         # Displaying detailed errors is not safe so remove the below line when ready to deploy
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
      
      if len(mobile_number) != 10:
         return apology("Mobile number must be of 10 digits", 403)

      # Check if the file is an audio file
      allowed_audio_types = {
         'audio/mpeg',  # MP3
         'audio/wav',   # WAV
         'audio/ogg',   # OGG
         'audio/x-wav', # Another variant of WAV
         'audio/webm',  # WebM audio
         'audio/flac'   # FLAC audio
      }

      if audio.mimetype not in allowed_audio_types:
         flash("Invalid audio file type", "danger")
         return redirect(url_for("book"))

    #   # Ensure upload directory exists
    #   upload_directory = os.path.join(os.getcwd(), 'uploads')
    #   if not os.path.exists(upload_directory):
    #      os.makedirs(upload_directory)

      audio_url = upload_get_tmp(audio)  

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
         # flash("Form submitted successfully!", "success")
         # return redirect(url_for("book"))

      except Exception as e:
         db.session.rollback()
         # return apology("An Error Occured", 500)
         # Displaying detailed errors is not safe so remove the below line when ready to deploy
         flash(f"An error occurred: {str(e)}", "danger")
         # Do not redirect to book page so that the user does not have to fill the form again
         return redirect(url_for("book"))
         
      flash("Thank You for Submitting Form We Will Get Back to you Soon.")

      return redirect(url_for("book"))

   else:
      return render_template("book.html")


@app.route("/team", methods=["GET", "POST"])
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
      
      if len(mobile_number) != 10:
         return apology("Mobile number must be of 10 digits", 403)

    #   file_path = os.path.join('uploads', aadhar_card.filename)
    #   aadhar_card.save(file_path)

    #   # Generate the URL
    #   aadhar_card_url = f"/uploads/{aadhar_card.filename}"

    #   file_path = os.path.join('uploads', pan_card.filename)
    #   pan_card.save(file_path)

    #   # Generate the URL
    #   pan_card_url = f"/uploads/{pan_card.filename}"

    #   file_path = os.path.join('uploads', photo.filename)
    #   photo.save(file_path)

    #   # Generate the URL
    #   photo_url = f"/uploads/{photo.filename}"
      aadhar_card_url = upload_get_tmp(aadhar_card)  
      pan_card_url = upload_get_tmp(pan_card)
      photo_url = upload_get_tmp(photo)


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
         # return apology("An Error Occured", 500)
         # Displaying detailed errors is not safe so remove the below line when ready to deploy
         return f"An error occurred: {str(e)}"

      flash("Thank You for Submitting Form We Will Get Back to you Soon.")

      return redirect(url_for("book"))

   else:
      return render_template("team.html")

   


@app.route("/initiative")
def initiative():
   return render_template("initiative.html")


@app.errorhandler(404)
def page_not_found(e):
   return apology("Page Not Found", 404)


@app.errorhandler(500)
def server_error(e):
   return apology("Internal Server Error", 500)



@app.route("/testing")
def testing():
   rows = db.session.execute(
      text(
         "SELECT photo_url FROM blind WHERE id = 8"
      ),
   ).fetchall()
   image = rows[0][0]
   return f"{image}"


if __name__ == "__main__":
    app.run(debug=True)


# Change code like below when ready to deploy 

# import logging
# from logging.handlers import RotatingFileHandler

# Set up logging
# handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.ERROR)
# formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
# handler.setFormatter(formatter)
# app.logger.addHandler(handler)

# from flask import Flask, render_template, flash, redirect, url_for

# app = Flask(__name__)

# @app.route('/some_route')
# def some_route():
#     try:
#         # Your route logic here
#         pass
#     except Exception as e:
#         app.logger.error(f"An error occurred: {str(e)}")
#         flash("An unexpected error occurred. Please try again later.", "danger")
#         return redirect(url_for('error'))

# @app.errorhandler(500)
# def internal_error(error):
#     app.logger.error(f"Server Error: {str(error)}")
#     return render_template('500.html'), 500

# @app.errorhandler(Exception)
# def unhandled_exception(e):
#     app.logger.error(f"Unhandled Exception: {str(e)}")
#     return render_template('500.html'), 500

# if __name__ == "__main__":
#     app.run(debug=False)

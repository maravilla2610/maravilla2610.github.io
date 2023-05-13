# -*- coding: utf-8 -*-

#create database for registered people and their emails and phone numbers   
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from google.cloud import bigquery
import requests 
import json 
import os
import base64
import tempfile 
from google.oauth2.service_account import Credentials
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


# Get the Google Cloud credentials from the environment variable

credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
if credentials is not None:
    credentials_dict = json.loads(credentials)  # This should create a dictionary
    _, path = tempfile.mkstemp()
    with open(path, 'w') as file:
        json.dump(credentials_dict, file)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path

client = bigquery.Client()  # This should now use the service account key file specified by the 'GOOGLE_APPLICATION_CREDENTIALS' environment variable

app = Flask(__name__, template_folder='templates')

# Check if we are running on Heroku
if os.getenv('DATABASE_URL') is None:
    # We are running on a local machine
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///registros.db"
else:
    # We are running on Heroku
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app) # initialize the database connection

#create a data base for the phone number and email of the registered people 
class Registro(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True) #
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

# Form submission handler
@app.route('/submit', methods=['POST']) # Replace this with your own code 
def submit():
    # Store input values in variables
    email = request.form['email']
    phone = request.form['phone']
    
    if not email or not phone:
        logging.error('Email or phone not provided')
        return redirect(url_for('error'))

   # Check if the user has already registered
    registro = Registro.query.filter_by(email=email, phone_number=phone).first() # check if the user has already registered in the database
    if registro:
        # The user has already registered
        return redirect(url_for('already_registered'))
    else:
        # The user has not already registered
        # Register the user in the database
        new_registro = Registro(email=email, phone_number=phone)
        db.session.add(new_registro)
        db.session.commit()

         #insert the data into BigQuery
        try:
            client = bigquery.Client()
            table_id = "colmena-386419.Registros.Nuevos1" #table id of the table in BigQuery
            
            rows_to_insert = [
                {"id":new_registro.id,"email": email, "phone_number": phone},
            ]

            errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
            if errors == []:
                print("New rows have been added.")
            else:
                print("Encountered errors while inserting rows: {}".format(errors))
        except Exception as e:
            print(e)

        #redirect the user to a page that tells them that they have been registered successfully
        return redirect(url_for('thank_you'))
        # Redirect the user to a page that tells them that they have been registered successfully
        
@app.route('/thank_you') #redirección al html de thank you para los nuevos usuarios 
def thank_you():
    return render_template('thank_you.html')
@app.route('/already_registered') #redirect to the html of already registered for the users that are already registered
def already_registered():   
    return render_template('already_registered.html')
@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)

#create database for registered people and their emails and phone numbers   
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests 
import json 


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///registros.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app) # initialize the database connection

#create a data base for the phone number and email of the registered people 
class Registro(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True) #
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

# Form submission handler
@app.route('/submit', methods=['POST']) # Replace this with your own code 
def submit():
    # Store input values in variables
    email = request.form['email']
    phone = request.form['phone']

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

        # Redirect the user to a page that tells them that they have been registered successfully

        return redirect(url_for('thank_you'))
        

@app.route('/thank_you') #redirección al html de thank you para los nuevos usuarios 
def thank_you():
    return render_template('thank_you.html')
@app.route('/already_registered') #redirect to the html of already registered for the users that are already registered
def already_registered():   
    return render_template('already_registered.html')


if __name__ == '__main__':
    app.run(debug=True)

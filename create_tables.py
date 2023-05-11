from flask import Flask, render_template, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from app import app, db, Registro

with app.app_context():
# Drop all registrations from the database
   # Import the database module
    db.create_all() # Create the tables according to the models in Colmena_Start/create_tables.py

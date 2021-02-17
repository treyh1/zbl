from flask import Flask
from app import app

@app.route('/')
def display_home():
	return render_template("home.html")
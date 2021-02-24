from flask import Flask, render_template, request
from app import app
import zibble2

@app.route('/')
def display_home():
	return render_template("home.html")

@app.route('/upload')
def upload_and_run():
	for file in request.files:
		file = request.files['file']
		zibble2.run_script_in_web_app(file)

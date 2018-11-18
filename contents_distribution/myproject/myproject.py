from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS,cross_origin
import json
import requests
from pathlib import Path
from datetime import datetime
from hashlib import sha256
application = Flask(__name__)
cors = CORS(application, supports_credentials=True, resources={r"/*": {"origins": "*"}})

@application.route("/")
def home():
		r = render_template('home.html')
		return r

@application.route("/log", methods=['POST'])
def log():
		payload = request.json
		print(payload)
		r = requests.post('http://localhost:8000/log', json=payload)
		print(r.text)
		return 'ok'

if __name__ == "__main__":
		application.run(host='0.0.0.0')

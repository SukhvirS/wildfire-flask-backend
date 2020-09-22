from  flask import Flask, escape, request
from  flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'This is the flask backend for the wildfire project'
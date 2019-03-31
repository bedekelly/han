from flask import Flask
from flask_cors import CORS

from .han import Han
from .model import initial_state

app = Flask(__name__)
CORS(app)
han = Han(app, initial_state, debug=True)

from . import update

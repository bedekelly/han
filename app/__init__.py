from flask import Flask
from .han import Han
from .model import initial_state

app = Flask(__name__)
han = Han(app, initial_state)

from . import update

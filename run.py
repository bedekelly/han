from flask import Flask
from han import Han

app = Flask(__name__)
han = Han(app)

import model
import views

app.run(debug=True)

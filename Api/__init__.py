from flask import Blueprint
from flaskext.mysql import MySQL

# Create a Blueprint for the payment API
payment_bp = Blueprint('payment', __name__, url_prefix='/api')

# Initialize Flask-MySQL extension
mysql = MySQL()



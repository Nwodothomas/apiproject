from flask import Flask
from flask_mysqldb import MySQL
from flask_mail import Mail

# Create Flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e34db6964b405a8f9f62d32a7ce9fe33'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'greatman'
app.config['MYSQL_DB'] = 'sendpayapi_db'
mysql = MySQL(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'ae372ba3fc7338'
app.config['MAIL_PASSWORD'] = 'd181b79c034ae0'
app.config['MAIL_DEFAULT_SENDER'] = 'nwodothomas@gmail.com'
mail = Mail(app)

# Import your routes after creating the Flask app
from app import routes

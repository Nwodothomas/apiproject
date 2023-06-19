from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Blueprint
from decimal import Decimal
import mysql.connector
import bcrypt
import os
import sys
from utils import get_navigation_links

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e34db6964b405a8f9f62d32a7ce9fe33'

# Register the payment blueprint with URL prefix
payment_bp = Blueprint('payment', __name__)
api = Api(payment_bp)

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

# Serializer for generating email verification tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Define the Swagger UI blueprint
SWAGGER_URL = '/api/docs'  # URL for accessing the Swagger UI page
API_URL = '/api/swagger.json'  # URL for accessing the Swagger JSON file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sendpayapi"  # Custom name for your app
    }
)

# Register the Swagger UI blueprint
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL, name='swagger_ui_blueprint')

# Define the payment model
payment_model = api.model('Payment', {
    'amount': fields.Float(required=True, description='The payment amount'),
    'currency': fields.String(required=True, description='The payment currency'),
    'payment_method': fields.Raw(required=True, description='The payment method')
})

# Create a namespace for the payment API
payment_ns = api.namespace('payment', description='Payment operations')

@app.route('/')
def index():
    if session.get('logged_in'):
        # User is logged in, display index page
        return render_template('index.html')
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve registration form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  # Add this line to capture the email field

        # Generate a new salt value
        salt = bcrypt.gensalt().decode('utf-8')

        # Hash the password with the salt
        salted_password = password.encode('utf-8') + salt.encode('utf-8')
        hashed_password = bcrypt.hashpw(salted_password, bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO registers(username, password, salt, email, email_verified) VALUES(%s, %s, %s, %s, %s)',
               (username, hashed_password, salt, email, False)) # Update the query to include the email field
        mysql.connection.commit()
        cursor.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT password, salt FROM registers WHERE username = %s', (username,))
        result = cursor.fetchone()

        if result:
            hashed_password = result[0].encode('utf-8')
            salt = result[1].encode('utf-8')

            salted_password = password.encode('utf-8') + salt
            if bcrypt.checkpw(salted_password, hashed_password):
                session['logged_in'] = True
                session['username'] = username
                flash('You have successfully logged in!', 'success')
                return redirect(url_for('payment'))  # Redirect to index page on successful login

        flash('Invalid username or password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE registers SET email_verified = %s WHERE email = %s", (True, email))
        mysql.connection.commit()
        cursor.close()
        flash('Email verified. You can now log in.', 'success')
    except:
        flash('Invalid or expired verification link', 'error')

    return redirect(url_for('login'))


def send_email(recipient, subject, body):
    message = Message(subject, recipients=[recipient])
    message.body = body
    mail.send(message)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/developers-portal')
def developers_portal():
    return render_template('developers-portal.html')

# Create Payment API endpoint
@api.route('/create_payment')
class CreatePayment(Resource):
    @api.expect(api.model('Payment', {
        'amount': fields.Float(required=True),
        'currency': fields.String(required=True),
        'payment_method': fields.String(required=True)
    }), validate=True)
    def post(self):
        data = api.payload
        amount = data.get('amount')
        currency = data.get('currency')
        payment_method = data.get('payment_method')

        # Perform necessary validations on the payment details
        if not amount or not currency or not payment_method:
            return {'error': 'Invalid payment details'}, 400

        # Perform the necessary database operations to create a new payment transaction
        try:
            # Get a database connection
            conn = mysql.connection
            cursor = conn.cursor()

            # Convert amount to Decimal
            amount = Decimal(amount)

            # Execute the SQL query to insert the payment details into the database
            query = "INSERT INTO payments (amount, currency, payment_method) VALUES (%s, %s, %s)"
            values = (amount, currency, payment_method)
            cursor.execute(query, values)
            conn.commit()

            # Get the auto-generated payment transaction ID
            payment_id = cursor.lastrowid

            # Close the cursor
            cursor.close()

            # Redirect to the Swagger UI page
            return redirect(url_for('swagger_ui_blueprint.show'))

        except Exception as e:
            return {'error': str(e)}, 500

    def get(self):
        return redirect(url_for('payment.doc'))

# Retrieve Payment API endpoint
@api.route('/payments/<int:payment_id>')
class RetrievePayment(Resource):
    def get(self, payment_id):
        try:
            # Get a database connection
            conn = mysql.connection
            cursor = conn.cursor()

            # Execute the SQL query to retrieve the payment details by payment ID
            query = "SELECT * FROM payments WHERE ID = %s"
            cursor.execute(query, (payment_id,))
            result = cursor.fetchone()

            # Check if the payment ID exists
            if result is None:
                return {'error': 'Payment not found'}, 404

            # Create a dictionary with the payment details
            payment_details = {
                'ID': result[0],
                'Amount': float(result[1]),  # Convert Decimal to float
                'Currency': result[2],
                'Payment_method': result[3]
            }

            # Close the cursor
            cursor.close()

            # Return the payment details
            return payment_details

        except Exception as e:
            return {'error': str(e)}, 500
        

# Define the UpdatePayment resource
@api.route('/payments/<int:payment_id>')
class UpdatePayment(Resource):
    @api.expect(api.model('UpdatePayment', {
        'status': fields.String(required=False),
        'additional_info': fields.String(required=False)
    }), validate=True)
    def put(self, payment_id):
        data = api.payload
        status = data.get('status')
        additional_info = data.get('additional_info')

        # Perform necessary validations on the updated payment details
        if not status and not additional_info:
            return {'error': 'No update data provided'}, 400

        # Perform the necessary database operations to update the payment transaction
        try:
            # Get a database connection
            conn = mysql.connection
            cursor = conn.cursor()

            # Execute the SQL query to update the payment details in the database
            query = "UPDATE payments SET status = %s, additional_info = %s WHERE ID = %s"
            values = (status, additional_info, payment_id)
            cursor.execute(query, values)
            conn.commit()

            # Close the cursor
            cursor.close()

            # Return a success message
            return {'message': 'Payment updated successfully'}

        except Exception as e:
            return {'error': str(e)}, 500
        
# Define the CancelPayment resource        
@api.route('/payments/<int:payment_id>')
class CancelPayment(Resource):
    def delete(self, payment_id):
        try:
            # Get a database connection
            conn = mysql.connection
            cursor = conn.cursor()

            # Check if the payment ID exists
            query = "SELECT * FROM payments WHERE ID = %s"
            cursor.execute(query, (payment_id,))
            result = cursor.fetchone()

            if result is None:
                return {'error': 'Payment not found'}, 404

            # Execute the SQL query to delete the payment transaction
            query = "DELETE FROM payments WHERE ID = %s"
            cursor.execute(query, (payment_id,))
            conn.commit()

            # Close the cursor
            cursor.close()

            # Return the cancellation confirmation
            return {'message': 'Payment cancelled successfully'}

        except Exception as e:
            return {'error': str(e)}, 500

# Define the ListPayments resource
@api.route('/payments')
class ListPayments(Resource):
    def get(self):
        try:
            # Get a database connection
            conn = mysql.connection
            cursor = conn.cursor()

            # Execute the SQL query to retrieve all payment transactions
            query = "SELECT ID, amount, currency, payment_method FROM payments"
            cursor.execute(query)
            results = cursor.fetchall()

            # Create a list to store payment details
            payments = []

            # Iterate over the results and create a dictionary for each payment
            for result in results:
                payment = {
                    'ID': result[0],
                    'amount': float(result[1]),
                    'currency': result[2],
                    'payment_method': result[3]
                }
                payments.append(payment)

            # Close the cursor
            cursor.close()

            # Return the list of payment transactions
            return {'payments': payments}

        except Exception as e:
            return {'error': str(e)}, 500


# Define the PaymentCallback resource
@api.route('/payments/callback', methods=['POST'])
class PaymentCallback(Resource):
    def post(self):
        try:
            # Get the callback data from the request body
            callback_data = request.get_json()

            # Extract relevant information from the callback data
            payment_id = callback_data.get('payment_id')
            status = callback_data.get('status')

            # Retrieve the payment transaction from the database using the payment_id
            conn = mysql.connection
            cursor = conn.cursor()

            query = "SELECT * FROM payments WHERE id = %s"
            cursor.execute(query, (payment_id,))
            payment = cursor.fetchone()

            # Check if the payment transaction exists
            if payment is None:
                return {'error': 'Payment not found'}, 404

            # Update the payment status based on the callback data
            query = "UPDATE payments SET status = %s WHERE id = %s"
            cursor.execute(query, (status, payment_id))
            conn.commit()

            # Perform any additional necessary actions based on the callback data
            if status == 'completed':
                # Example: Update the user's account balance
                user_id = payment[5]  # Assuming the user_id is in the 6th column
                query = "SELECT * FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                user = cursor.fetchone()

                if user is not None:
                    user_balance = user[3]  # Assuming the balance is in the 4th column
                    user_balance += payment[1]  # Assuming the amount is in the 2nd column

                    query = "UPDATE users SET balance = %s WHERE id = %s"
                    cursor.execute(query, (user_balance, user_id))
                    conn.commit()

                # Example: Trigger other business processes or workflows

            # Close the cursor and database connection
            cursor.close()
            conn.close()

            # Return a confirmation of successful processing of the callback
            return {'message': 'Callback processed successfully'}

        except Exception as e:
            return {'error': str(e)}, 500
# Define the RefundPayment resource
@api.route('/payments/<int:payment_id>/refund', methods=['POST'])
class RefundPayment(Resource):
    def post(self, payment_id):
        try:
            # Retrieve the payment transaction from the database using the payment_id
            conn = mysql.connection
            cursor = conn.cursor()

            query = "SELECT * FROM payments WHERE id = %s"
            cursor.execute(query, (payment_id,))
            payment = cursor.fetchone()

            # Check if the payment transaction exists
            if payment is None:
                return {'error': 'Payment not found'}, 404

            # Perform the necessary actions to refund the payment
            # Example: Update the payment status to 'refunded' in the database
            query = "UPDATE payments SET status = %s WHERE id = %s"
            cursor.execute(query, ('refunded', payment_id))
            conn.commit()

            # Perform any additional necessary actions for the refund process
            # Example: Reverse the amount from the user's account balance

            # Close the cursor
            cursor.close()

            # Return a confirmation of the refund
            return {'message': 'Payment refunded successfully'}

        except Exception as e:
            return {'error': str(e)}, 500


app.register_blueprint(payment_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)







'''
Imports the modules and functions for handling Flask requests, 
rendering templates, and accessing the payment blueprint. 
Imports the get_navigation_links function from the utils module.
'''
from flask import request, jsonify, render_template
from . import payment_bp
from utils import get_navigation_links

# Create Payment endpoint
@payment_bp.route('/payment', methods=['POST'])
def create_payment():
    # Rest of the code
    # Retrieve payment details from the request body
    amount = request.form.get('amount')
    currency = request.form.get('currency')
    payment_method = request.form.get('payment_method')

    # Perform necessary validations on the payment details
    if not amount or not currency or not payment_method:
        return jsonify({'error': 'Invalid payment details'}), 400

    # Perform the necessary database operations to create a new payment transaction
    try:
        # Get a database connection
        conn = payment_bp.mysql.connect()
        cursor = conn.cursor()

        # Execute the SQL query to insert the payment details into the database
        query = "INSERT INTO payments (amount, currency, payment_method) VALUES (%s, %s, %s)"
        values = (amount, currency, payment_method)
        cursor.execute(query, values)
        conn.commit()

        # Get the auto-generated payment transaction ID
        payment_id = cursor.lastrowid

        # Close the cursor and database connection
        cursor.close()
        conn.close()

        # Get the navigation links from the utils.py using the imported function
        navigation_links = get_navigation_links()

        # Render the payment.html template with the navigation links and payment ID
        return render_template('api/payment.html', navigation_links=navigation_links, payment_id=payment_id)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import render_template, session, request, redirect, url_for, flash
from itsdangerous import Serializer
import bcrypt
from app import mysql


def landing():
    if session.get('logged_in'):
        # User is logged in, display index.html
        return render_template('index.html')
    else:
        # User is not logged in, display login.html
        return render_template('login.html')

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
                return redirect(url_for('payment.doc'))  # Redirect to paymentapi swagger ui page on successful login

        flash('Invalid username or password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

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

def dashboard():
    return render_template('dashboard.html')

def developers_portal():
    return render_template('developers-portal.html')

def index():
    return render_template('index.html')

def view_documentation():
    return render_template('/doc/doc.html')

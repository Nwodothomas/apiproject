#!/usr/bin/python3
'''
Import the subprocess module to execute 
pip commands from within the script
Define a list called packages that contains 
the names of the required packages.
'''
import subprocess

''' List of required packages '''
packages = [
    'flask',
    'flask-mysqldb',
    'passlib',
    'flask-wtf',
    'wtforms',
    'flask-login',
    'flask-bcrypt',
    'flask-session',
    'flask-cors',
    'mysql-connector-python'
]

'''Install each package using pip '''
for package in packages:
    subprocess.call(['pip', 'install', package])

print("Package installation completed successfully.")

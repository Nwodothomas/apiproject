#!/usr/bin/python3

''' 
This code generates a secure random secret 
key using the secrets module and prints it 
to the console
'''

import secrets

secret_key = secrets.token_hex(16)
print(secret_key)

 
# To test your API by sending a request from another Python script
# import request

import requests

# Define the necessary variables for your request, such as the API URL and the data to send in the request body

url = 'http://127.0.0.1:5000/api/create_payment'  
data = {
    'amount': 100,
    'currency': 'USD',
    'payment_method': 'credit_card'
}

# Send a POST request to your API endpoint using the requests.post() method
response = requests.post(url, data=data)

# Handle the response returned by the API
if response.status_code == 200:
    # Request was successful
    print('Payment created successfully')
else:
    # Request failed
    print('Failed to create payment')
    print('Response:', response.text)


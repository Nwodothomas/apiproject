from flask import url_for

# Function to get navigation links
def get_navigation_links(api_links=None):
    # Define your navigation links here
    links = [
        {'url': url_for('index'), 'label': 'Home'},
        {'url': url_for('register'), 'label': 'Register'},
        {'url': url_for('login'), 'label': 'Login'},
        {'url': url_for('developers_portal'), 'label': 'Developers'},
        {'url': url_for('dashboard'), 'label': 'Dashboard'},
        {'url': url_for('payment_bp.create_payment'), 'label': 'Create Payment'},
        # Add more navigation links as needed
    ]
    
    # Add API-specific navigation links
    if api_links:
        links.extend(api_links)
    
    return links


'''from flask import url_for


# Function to get navigation links
def get_navigation_links():
    # Define your navigation links here
    links = [
        {'url': url_for('index'), 'label': 'Home'},
        {'url': url_for('register'), 'label': 'Register'},
        {'url': url_for('login'), 'label': 'Login'},
        {'url': url_for('developers_portal'), 'label': 'Developers'},
        {'url': url_for('dashboard'), 'label': 'Dashboard'},
        {'url': url_for('payment_bp.create_payment'), 'label': 'Create Payment'},
        # Add more navigation links as needed
    ]
    return links
    '''

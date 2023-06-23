from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.is_verified = False

    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}')"

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)

    def __init__(self, amount, currency, description, customer_id):
        self.amount = amount
        self.currency = currency
        self.description = description
        self.customer_id = customer_id

    def __repr__(self):
        return f"Payment(amount={self.amount}, currency='{self.currency}', description='{self.description}')"

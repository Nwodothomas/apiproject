
from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint
from decimal import Decimal
import bcrypt

from app import app, mysql
from .views import landing, register, login, verify_email, dashboard, developers_portal, index, view_documentation

# Register the payment blueprint with URL prefix
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Swagger API documentation
payment_swagger_ui_blueprint = get_swaggerui_blueprint(
    '/payment/docs',
    '/payment/swagger.json',
    config={
        'app_name': "Payment API"
    }
)

@payment_bp.route('/doc')
def payment_doc():
    return redirect(url_for('payment.payment_swagger_ui'))

@payment_bp.route('/swagger.json')
def payment_swagger():
    return payment_api.__schema__

payment_api = Api(payment_bp, version='1.0', title='Payment API', doc='/docs')

ns = payment_api.namespace('payment', description='Payment operations')

payment_model = payment_api.model('Payment', {
    'amount': fields.Float(required=True, description='Payment amount'),
    'currency': fields.String(required=True, description='Currency code (e.g., USD)'),
    'description': fields.String(required=True, description='Payment description'),
    'customer_id': fields.Integer(required=True, description='Customer ID')
})

payments = {}  # Placeholder for payments data

@ns.route('/')
class PaymentResource(Resource):
    @ns.expect(payment_model)
    def post(self):
        data = payment_api.payload
        payment_id = len(payments) + 1
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        customer_id = data['customer_id']

        # Perform payment processing logic here
        # ...

        # Store payment data
        payment_data = {
            'payment_id': payment_id,
            'amount': amount,
            'currency': currency,
            'description': description,
            'customer_id': customer_id
        }
        payments[payment_id] = payment_data

        # Return response
        response = {
            'status': 'success',
            'message': 'Payment processed successfully',
            'payment_id': payment_id,
            'amount': amount,
            'currency': currency,
            'description': description,
            'customer_id': customer_id
        }
        return response

@ns.route('/<int:payment_id>')
class SinglePaymentResource(Resource):
    def get(self, payment_id):
        if payment_id in payments:
            return payments[payment_id]
        else:
            return {'status': 'error', 'message': 'Payment not found'}, 404

    @ns.expect(payment_model)
    def put(self, payment_id):
        if payment_id in payments:
            data = payment_api.payload
            amount = data['amount']
            currency = data['currency']
            description = data['description']
            customer_id = data['customer_id']

            # Update payment data
            payments[payment_id]['amount'] = amount
            payments[payment_id]['currency'] = currency
            payments[payment_id]['description'] = description
            payments[payment_id]['customer_id'] = customer_id

            # Return response
            response = {
                'status': 'success',
                'message': 'Payment updated successfully',
                'payment_id': payment_id,
                'amount': amount,
                'currency': currency,
                'description': description,
                'customer_id': customer_id
            }
            return response
        else:
            return {'status': 'error', 'message': 'Payment not found'}, 404

    def delete(self, payment_id):
        if payment_id in payments:
            del payments[payment_id]
            return {'status': 'success', 'message': 'Payment deleted successfully'}
        else:
            return {'status': 'error', 'message': 'Payment not found'}, 404

@ns.route('/list')
class PaymentsListResource(Resource):
    def get(self):
        return {'payments': list(payments.values())}

@ns.route('/<int:payment_id>/cancel')
class CancelPaymentResource(Resource):
    def post(self, payment_id):
        if payment_id in payments:
            # Check if payment is already canceled
            if payments[payment_id].get('status') == 'canceled':
                return {'status': 'error', 'message': 'Payment is already canceled'}, 400

            # Perform cancellation logic
            # ...

            # Update payment status
            payments[payment_id]['status'] = 'canceled'

            return {'status': 'success', 'message': 'Payment canceled successfully'}
        else:
            return {'status': 'error', 'message': 'Payment not found'}, 404


@ns.route('/<int:payment_id>/refund')
class RefundPaymentResource(Resource):
    def post(self, payment_id):
        if payment_id in payments:
            # Check if payment is already refunded
            if payments[payment_id].get('status') == 'refunded':
                return {'status': 'error', 'message': 'Payment is already refunded'}, 400

            # Perform refund logic
            # ...

            # Update payment status
            payments[payment_id]['status'] = 'refunded'

            return {'status': 'success', 'message': 'Payment refunded successfully'}
        else:
            return {'status': 'error', 'message': 'Payment not found'}, 404


@ns.route('/callback')
class PaymentCallbackResource(Resource):
    def post(self):
        # Extract callback data from the request
        callback_data = payment_api.payload

        # Retrieve payment details from the callback data
        payment_id = callback_data.get('payment_id')
        status = callback_data.get('status')

        # Check if payment exists
        if payment_id in payments:
            # Update payment status based on the callback status
            payments[payment_id]['status'] = status

            # Perform additional actions based on the callback status
            if status == 'success':
                # Payment succeeded
                # Perform success actions
                pass
            elif status == 'failed':
                # Payment failed
                # Perform failure actions
                pass

            return {'status': 'success', 'message': 'Payment callback processed successfully'}
        else:
            return {'status': 'error', 'message': 'Payment not found'}, 404

# Register routes
app.register_blueprint(payment_bp)
app.register_blueprint(payment_swagger_ui_blueprint, url_prefix='/payment/docs')
app.add_url_rule('/', 'landing', landing)
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/verify_email/<token>', 'verify_email', verify_email)
app.add_url_rule('/dashboard', 'dashboard', dashboard)
app.add_url_rule('/developers-portal', 'developers_portal', developers_portal)
app.add_url_rule('/index', 'index', index)
app.add_url_rule('/view_documentation', 'view_documentation', view_documentation)
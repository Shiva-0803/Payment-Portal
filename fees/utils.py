import razorpay
from django.conf import settings

def create_razorpay_order(amount, currency='INR', receipt=None, notes=None):
    """
    Create a Razorpay Order.
    Amount should be in paisa (i.e., Rs * 100).
    """
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    data = {
        'amount': int(amount * 100), # Amount in paisa
        'currency': currency,
        'receipt': receipt,
        'notes': notes or {}
    }
    
    order = client.order.create(data=data)
    return order

def verify_razorpay_payment_signature(params):
    """
    Verify the payment signature.
    params: dict containing razorpay_order_id, razorpay_payment_id, razorpay_signature
    """
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    try:
        client.utility.verify_payment_signature(params)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False

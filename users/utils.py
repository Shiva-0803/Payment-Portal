import requests
import os
import random

def generate_otp():
    """Generates a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

from django.core.mail import send_mail
from django.conf import settings

def send_email_otp(email, otp):
    """
    Sends an OTP to the given email address.
    
    Args:
        email (str): The recipient's email address.
        otp (str): The 6-digit OTP to send.
        
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    subject = 'Your Login OTP for Exam Portal'
    message = f'Your OTP for login is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending Email: {e}")
        return False

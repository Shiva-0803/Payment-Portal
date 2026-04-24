import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from django.test import Client
from users.models import CustomUser

def test_login():
    client = Client()
    
    # Ensure Exam user exists
    email = 'exam@example.com'
    if not CustomUser.objects.filter(email=email).exists():
        user = CustomUser.objects.create_user(email=email, password='password123')
        user.is_exam_branch = True
        user.is_staff = True
        user.save()
        print("Created exam user")
    
    # 1. Login to get OTP
    res1 = client.post('/users/login/', {'email': email})
    print("Login Response Status:", res1.status_code)
    assert res1.status_code == 302
    
    otp = client.session.get('auth_otp')
    print("OTP:", otp)
    
    # 2. Submit OTP
    res2 = client.post('/users/otp/', {'otp': otp})
    print("OTP Verify Status:", res2.status_code)
    # Redirects to verify-password
    assert res2.status_code == 302
    assert res2.url == '/users/verify-password/'
    
    # 3. Submit password
    res3 = client.post('/users/verify-password/', {'password': 'password123'})
    print("Password Verify Status:", res3.status_code)
    
    if res3.status_code == 302:
        print("Redirected to:", res3.url)
    else:
        print(res3.content)

if __name__ == '__main__':
    test_login()

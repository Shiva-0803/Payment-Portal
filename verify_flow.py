import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from django.test import Client
from users.models import CustomUser, StudentProfile
from fees.models import Exam, Transaction

def verify_flow():
    client = Client()
    mobile = '9876543210'
    
    # 1. Login (Get OTP)
    print("Testing Login...")
    response = client.post('/users/login/', {'mobile_number': mobile})
    assert response.status_code == 302
    
    # Get OTP from session (simulating retrieving from console)
    otp = client.session['auth_otp']
    print(f"Captured OTP: {otp}")
    
    # 2. Verify OTP
    session = client.session
    session['auth_mobile'] = mobile
    session['auth_otp'] = otp
    session.save()
    
    response = client.post('/users/otp/', {'otp': otp})
    assert response.status_code == 302
    
    user = CustomUser.objects.get(mobile_number=mobile)
    
    # 3. Register Student if not exists
    if not hasattr(user, 'student_profile'):
        print("Registering Student...")
        client.force_login(user) 
        response = client.post('/users/register/', {
            'roll_number': '21A91A0501',
            'branch': 'CSE',
            'year': 3
        })
        assert response.status_code == 302
    else:
         client.force_login(user)

    # Setup Exam
    defaults = {
        'fee_regular': 1200, 
        'fee_supply_small': 600,
        'fee_supply_large': 1100
    }
    
    exam, created = Exam.objects.get_or_create(
        name='Semester 3', 
        semester=3,
        defaults=defaults
    )
    if not created:
        exam.fee_regular = 1200
        exam.fee_supply_small = 600
        exam.fee_supply_large = 1100
        exam.save()
    
    # 4. Select Exam (Regular)
    print("Testing Regular Exam Selection...")
    response = client.post(f'/fees/select/{exam.id}/', {'exam_category': 'REGULAR'})
    txn = Transaction.objects.filter(student=user, exam=exam, exam_type='REGULAR').last()
    assert float(txn.amount) == 1200.0
    
    # 5. Select Exam (Supply Small - 2 Subjects)
    print("Testing Supply <= 2 Subjects...")
    response = client.post(f'/fees/select/{exam.id}/', {'exam_category': 'SUPPLY', 'subject_count': 2})
    txn = Transaction.objects.filter(student=user, exam=exam).order_by('-id').first()
    assert float(txn.amount) == 600.0
    
    # 6. Select Exam (Supply Large - 3 Subjects)
    print("Testing Supply > 2 Subjects...")
    response = client.post(f'/fees/select/{exam.id}/', {'exam_category': 'SUPPLY', 'subject_count': 3})
    txn = Transaction.objects.filter(student=user, exam=exam).order_by('-timestamp').first() 
    # Grab latest
    assert float(txn.amount) == 1100.0
    
    print("ALL TESTS PASSED!")

if __name__ == '__main__':
    verify_flow()

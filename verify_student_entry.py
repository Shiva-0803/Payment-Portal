import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from users.models import StudentEntry

def test_student_entry():
    print("Testing StudentEntry Model and View...")
    
    # Clean up previous test data
    StudentEntry.objects.filter(roll_number='TEST101').delete()
    
    c = Client()
    
    # Test POST request to create a new entry
    response = c.post('/users/student-entry/', {
        'full_name': 'Test Student',
        'roll_number': 'TEST101',
        'branch': 'CSE',
        'year': 1,
        'mobile_number': '1234567890'
    })
    
    if response.status_code == 302:
        print("PASS: View redirected successfully (likely to home).")
    elif response.status_code == 200:
         print("WARNING: View returned 200 (Form might have errors). Checking errors...")
         # context = response.context # Context might not be available in all setups without middleware
         # print(response.content.decode())
    else:
        print(f"FAIL: Unexpected status code: {response.status_code}")

    # Verify data in DB
    try:
        student = StudentEntry.objects.get(roll_number='TEST101')
        print(f"PASS: StudentEntry retrieved from DB: {student}")
        print(f"Name: {student.full_name}, Branch: {student.branch}, Year: {student.year}")
    except StudentEntry.DoesNotExist:
        print("FAIL: StudentEntry not found in DB.")

    # Clean up
    student.delete()
    print("Test Complete.")

if __name__ == '__main__':
    test_student_entry()

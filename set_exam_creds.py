
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from users.models import CustomUser

email = 'kucet@1281'
password = 'kucet@2025'

try:
    user = CustomUser.objects.get(email=email)
    print(f"Updating existing user {email}")
except CustomUser.DoesNotExist:
    # Check if there is already an exam branch user, update them, otherwise create new
    exam_users = CustomUser.objects.filter(is_exam_branch=True)
    if exam_users.exists():
        user = exam_users.first()
        print(f"Updating existing Exam Branch user {user.email} to {email}")
        user.email = email
    else:
        print(f"Creating new Exam Branch user {email}")
        user = CustomUser(email=email)
        user.is_exam_branch = True
        user.is_staff = True # Give staff access so they can login via internal login

user.set_password(password)
user.is_exam_branch = True # Ensure it's set
user.save()

print(f"SUCCESS: Exam Branch credentials set to:\nEmail: {email}\nPassword: {password}")

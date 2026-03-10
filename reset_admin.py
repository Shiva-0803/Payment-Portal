
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from users.models import CustomUser

email = 'admin@kucet.com'
password = 'admin0803'

# Find existing superuser or create new
try:
    user = CustomUser.objects.get(email=email)
    print(f"Updating existing user {email}")
except CustomUser.DoesNotExist:
    # Check if ANY superuser exists to update, or just create new
    superusers = CustomUser.objects.filter(is_superuser=True)
    if superusers.exists():
        user = superusers.first()
        print(f"Updating existing superuser {user.email} to {email}")
        user.email = email
    else:
        print(f"Creating new superuser {email}")
        user = CustomUser(email=email)
        user.is_staff = True
        user.is_superuser = True

user.set_password(password)
user.save()

print(f"SUCCESS: Admin credentials set to:\nEmail: {email}\nPassword: {password}")

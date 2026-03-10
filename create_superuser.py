import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from users.models import CustomUser

email = 'admin@example.com'
password = '0803'

if not CustomUser.objects.filter(email=email).exists():
    CustomUser.objects.create_superuser(email=email, password=password)
    print(f"Superuser '{email}' created with password '{password}'.")
else:
    print(f"Superuser '{email}' already exists.")

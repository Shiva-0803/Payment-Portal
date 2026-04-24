import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from users.models import CustomUser

# 1. Admin / Superuser
admin_email = 'adminkucet@kucet.com'
admin_password = 'admin@0803'

admin_user, admin_created = CustomUser.objects.get_or_create(email=admin_email)
admin_user.set_password(admin_password)
admin_user.is_superuser = True
admin_user.is_staff = True
admin_user.save()
if admin_created:
    print(f"Superuser '{admin_email}' created.")
else:
    print(f"Superuser '{admin_email}' updated.")

# 2. Exam Branch User
exam_email = 'examkucet@kucet.com'
exam_password = 'exam@kucet'

exam_user, exam_created = CustomUser.objects.get_or_create(email=exam_email)
exam_user.set_password(exam_password)
exam_user.is_exam_branch = True
exam_user.is_staff = True  # Optional, but helps if they need basic admin panel access
exam_user.save()
if exam_created:
    print(f"Exam Branch User '{exam_email}' created.")
else:
    print(f"Exam Branch User '{exam_email}' updated.")

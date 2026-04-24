import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

from users.models import CustomUser

def sync_user(email, password, is_superuser=False, is_exam_branch=False):
    """Creates or updates a user with the given credentials and roles."""
    if not email or not password:
        print(f"Skipping {'Superuser' if is_superuser else 'Exam Branch'} sync: Email or Password not provided.")
        return

    user, created = CustomUser.objects.get_or_create(email=email)
    user.set_password(password)
    user.is_staff = True
    
    if is_superuser:
        user.is_superuser = True
    if is_exam_branch:
        user.is_exam_branch = True
        
    user.save()
    
    status = "created" if created else "updated"
    role = "Superuser" if is_superuser else "Exam Branch"
    print(f"SUCCESS: {role} user '{email}' {status}.")

if __name__ == "__main__":
    print("Starting credential synchronization...")
    
    # 1. Admin / Superuser
    # Using environment variables from Render, falling back to previous defaults
    admin_email = os.getenv('ADMIN_EMAIL', 'adminkucet@kucet.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin@0803')
    sync_user(admin_email, admin_password, is_superuser=True)

    # 2. Exam Branch User
    # Using environment variables from Render, falling back to previous defaults
    exam_email = os.getenv('EXAM_EMAIL', 'examkucet@kucet.com')
    exam_password = os.getenv('EXAM_PASSWORD', 'exam@kucet')
    sync_user(exam_email, exam_password, is_exam_branch=True)
    
    print("Credential synchronization completed.")

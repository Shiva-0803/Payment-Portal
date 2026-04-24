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
    print("--- Starting Credential Sync ---")
    
    # 1. Admin / Superuser
    admin_email_env = os.getenv('ADMIN_EMAIL')
    admin_password_env = os.getenv('ADMIN_PASSWORD')
    
    if admin_email_env and admin_password_env:
        print(f"Using Render Environment Variables for Admin: {admin_email_env}")
        sync_user(admin_email_env, admin_password_env, is_superuser=True)
    else:
        print("ADMIN_EMAIL or ADMIN_PASSWORD not set in Render. Using hardcoded defaults.")
        sync_user('adminkucet@kucet.com', 'admin@0803', is_superuser=True)

    # 2. Exam Branch User
    exam_email_env = os.getenv('EXAM_EMAIL')
    exam_password_env = os.getenv('EXAM_PASSWORD')
    
    if exam_email_env and exam_password_env:
        print(f"Using Render Environment Variables for Exam Branch: {exam_email_env}")
        sync_user(exam_email_env, exam_password_env, is_exam_branch=True)
    else:
        print("EXAM_EMAIL or EXAM_PASSWORD not set in Render. Using hardcoded defaults.")
        sync_user('examkucet@kucet.com', 'exam@kucet', is_exam_branch=True)
    
    print("--- Credential Sync Completed ---")

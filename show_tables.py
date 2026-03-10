import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_portal.settings')
django.setup()

def show_tables():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("\n--- Database Tables in 'exam_portal_db' ---\n")
        for table in tables:
            print(f"- {table[0]}")
            
        print("\n-------------------------------------------")
        print("NOTE: 'users_studentregistry' is where Admin entered students are stored.")
        print("NOTE: 'users_studentprofile' is where Registered User profiles are stored.")

if __name__ == "__main__":
    show_tables()

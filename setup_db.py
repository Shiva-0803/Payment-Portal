import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_db():
    password = '0803'
    db_name = "exam_portal_db"
    
    # List of users to try. 'postgres' is standard, 'postgrey' is what user typed (likely typo)
    users_to_try = ['postgres', 'postgrey']
    
    con = None
    connected_user = None

    print(f"Attempting to connect to PostgreSQL to create database: {db_name}...")

    for user in users_to_try:
        try:
            print(f"Trying to connect as user '{user}'...")
            con = psycopg2.connect(dbname='postgres', user=user, host='localhost', password=password, port='5432')
            connected_user = user
            print(f"Successfully connected as '{user}'.")
            break
        except psycopg2.OperationalError as e:
            print(f"Connection failed for '{user}': {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    if not con:
        print("Could not connect to PostgreSQL with provided credentials.")
        sys.exit(1)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    
    try:
        # Check if db exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        if exists:
             print(f"Database '{db_name}' already exists.")
        else:
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"Database '{db_name}' created successfully.")
    except Exception as e:
        print(f"Database creation failed: {e}")
        sys.exit(1)
    finally:
        cur.close()
        con.close()
    
    # Print the working username for the next step (parsing this output)
    print(f"VALID_USER:{connected_user}")

if __name__ == "__main__":
    try:
        create_db()
    except ImportError:
        print("Error: psycopg2 module not found. Please install it using 'pip install psycopg2-binary'")

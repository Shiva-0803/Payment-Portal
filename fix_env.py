content = """DB_NAME=exam_portal_db
DB_USER=postgres
DB_PASSWORD=0803
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY='django-insecure-custom-key-for-dev'
DEBUG=True

EMAIL_HOST_USER=kakatiya1821@gmail.com
EMAIL_HOST_PASSWORD=jgxixddxyurkgmmy
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
"""
with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed .env")

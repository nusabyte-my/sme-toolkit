import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

# Create default business profile
profile_id = 'default'
user_id = 'default_user'
company_name = 'Default Company'
industry = 'Technology'
business_stage = 'startup'

cursor.execute('''
    INSERT INTO business_profiles (id, user_id, company_name, industry, business_stage, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (profile_id, user_id, company_name, industry, business_stage, datetime.utcnow(), datetime.utcnow()))

conn.commit()
conn.close()

print(f"Created default business profile with ID: {profile_id}")

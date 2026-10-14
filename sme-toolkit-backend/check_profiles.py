import sqlite3

conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

print("Business profiles:")
cursor.execute('SELECT id, user_id, company_name, industry FROM business_profiles')
for row in cursor.fetchall():
    print(row)

conn.close()

import sqlite3

conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

print("Company goals columns:")
cursor.execute('PRAGMA table_info(company_goals)')
for row in cursor.fetchall():
    print(row)

conn.close()

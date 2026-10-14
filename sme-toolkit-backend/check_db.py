import sqlite3

conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

print("Business profiles columns:")
cursor.execute('PRAGMA table_info(business_profiles)')
for row in cursor.fetchall():
    print(row)

print("\nAnalytics metrics columns:")
cursor.execute('PRAGMA table_info(analytics_metrics)')
for row in cursor.fetchall():
    print(row)

print("\nScore records columns:")
cursor.execute('PRAGMA table_info(score_records)')
for row in cursor.fetchall():
    print(row)

conn.close()

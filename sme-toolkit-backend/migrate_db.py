import sqlite3

# Connect to the database
conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

# Add missing columns to business_profiles table
try:
    cursor.execute('ALTER TABLE business_profiles ADD COLUMN strategy_settings JSON')
    print("Added strategy_settings column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("strategy_settings column already exists")
    else:
        print(f"Error adding strategy_settings: {e}")

try:
    cursor.execute('ALTER TABLE business_profiles ADD COLUMN scoring_preferences JSON')
    print("Added scoring_preferences column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("scoring_preferences column already exists")
    else:
        print(f"Error adding scoring_preferences: {e}")

try:
    cursor.execute('ALTER TABLE business_profiles ADD COLUMN analytics_config JSON')
    print("Added analytics_config column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("analytics_config column already exists")
    else:
        print(f"Error adding analytics_config: {e}")

conn.commit()
conn.close()

print("\nMigration completed!")

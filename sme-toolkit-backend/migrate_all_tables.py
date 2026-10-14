import sqlite3

conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

# Add missing columns to company_goals table
missing_columns = {
    'category': 'VARCHAR',
    'smart_criteria': 'JSON',
    'bmc_alignment': 'JSON',
    'milestones': 'JSON',
    'success_metrics': 'JSON'
}

for column, col_type in missing_columns.items():
    try:
        cursor.execute(f'ALTER TABLE company_goals ADD COLUMN {column} {col_type}')
        print(f"Added {column} column to company_goals")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"{column} column already exists in company_goals")
        else:
            print(f"Error adding {column}: {e}")

conn.commit()
conn.close()

print("\nMigration completed!")

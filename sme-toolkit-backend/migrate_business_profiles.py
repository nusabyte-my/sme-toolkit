import sqlite3

conn = sqlite3.connect('sme_toolkit.db')
cursor = conn.cursor()

# Add missing columns to business_profiles table
missing_columns = {
    'business_type': 'VARCHAR',
    'legal_structure': 'VARCHAR',
    'registration_number': 'VARCHAR',
    'tax_id': 'VARCHAR',
    'founding_date': 'DATETIME',
    'website_url': 'VARCHAR',
    'business_description': 'TEXT',
    'mission_statement': 'TEXT',
    'vision_statement': 'TEXT',
    'business_address': 'JSON',
    'headquarters_location': 'JSON',
    'operating_locations': 'JSON',
    'team_size': 'INTEGER',
    'team_structure': 'JSON',
    'key_team_members': 'JSON',
    'annual_revenue': 'FLOAT',
    'revenue_currency': 'VARCHAR',
    'revenue_range': 'VARCHAR',
    'profit_margin': 'FLOAT',
    'funding_stage': 'VARCHAR',
    'funding_amount': 'FLOAT',
    'customer_count': 'INTEGER',
    'active_customers': 'INTEGER',
    'monthly_active_users': 'INTEGER',
    'customer_acquisition_cost': 'FLOAT',
    'customer_lifetime_value': 'FLOAT',
    'churn_rate': 'FLOAT',
    'products_services': 'JSON',
    'target_market': 'JSON',
    'competitive_advantages': 'JSON',
    'tech_stack': 'JSON',
    'software_tools': 'JSON',
    'integrations': 'JSON',
    'short_term_goals': 'JSON',
    'long_term_goals': 'JSON',
    'current_challenges': 'JSON',
    'growth_opportunities': 'JSON',
    'profile_completeness_score': 'FLOAT',
    'last_data_refresh': 'DATETIME',
    'data_quality_score': 'FLOAT'
}

for column, col_type in missing_columns.items():
    try:
        cursor.execute(f'ALTER TABLE business_profiles ADD COLUMN {column} {col_type}')
        print(f"Added {column} column to business_profiles")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"{column} column already exists in business_profiles")
        else:
            print(f"Error adding {column}: {e}")

conn.commit()
conn.close()

print("\nMigration completed!")

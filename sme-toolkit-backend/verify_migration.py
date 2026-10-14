"""
Verification script for enhanced data profiling migration
"""
import asyncio
from sqlalchemy import text
from app.database import engine


async def verify_tables():
    """Verify all tables exist and show their schemas"""
    tables_to_check = [
        'user_profiles',
        'social_media_profiles',
        'user_activity_logs',
        'privacy_settings',
        'profile_insights',
        'business_profiles'
    ]
    
    print("=" * 80)
    print("DATABASE MIGRATION VERIFICATION")
    print("=" * 80)
    print()
    
    async with engine.begin() as conn:
        # Check each table
        for table in tables_to_check:
            result = await conn.execute(
                text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            )
            exists = result.fetchone()
            
            if exists:
                print(f"[OK] Table '{table}' exists")
                
                # Show schema
                result = await conn.execute(text(f"PRAGMA table_info({table})"))
                columns = result.fetchall()
                print(f"  Columns ({len(columns)}):")
                for col in columns:
                    print(f"    - {col[1]} ({col[2]})")
                
                # Show indexes
                result = await conn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table}'")
                )
                indexes = result.fetchall()
                print(f"  Indexes ({len(indexes)}):")
                for idx in indexes:
                    print(f"    - {idx[0]}")
                print()
            else:
                print(f"[FAIL] Table '{table}' does NOT exist")
                print()
        
        # Check for data in business_profiles
        print("=" * 80)
        print("EXISTING DATA CHECK")
        print("=" * 80)
        print()
        
        result = await conn.execute(text("SELECT COUNT(*) FROM business_profiles"))
        count = result.fetchone()[0]
        print(f"Business profiles count: {count}")
        
        if count > 0:
            result = await conn.execute(text("SELECT * FROM business_profiles LIMIT 1"))
            row = result.fetchone()
            print(f"Sample business profile: {row}")
        
        print()
        print("=" * 80)
        print("VERIFICATION COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(verify_tables())

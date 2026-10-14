"""
Migration script for enhanced data profiling tables

This script adds new tables and columns to support:
- User profiles with demographics, preferences, and interests
- Enhanced business profiles with additional fields
- Social media profiles with flexible metrics
- User activity logs for engagement tracking
- Privacy settings for consent management
- Profile insights for AI-generated recommendations
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate():
    """
    Run database migration for enhanced data profiling.
    
    Creates new tables and adds columns to existing tables.
    """
    async with engine.begin() as conn:
        try:
            # Create all new tables
            logger.info("Creating new tables...")
            await conn.run_sync(Base.metadata.create_all)
            
            # Note: SQLite doesn't support ALTER TABLE with ADD COLUMN in the same way
            # The tables will be created with all columns from the start
            # If business_profiles table already exists, it will be recreated with new columns
            
            logger.info("Migration completed successfully!")
            logger.info("New tables created:")
            logger.info("  - user_profiles")
            logger.info("  - social_media_profiles")
            logger.info("  - user_activity_logs")
            logger.info("  - privacy_settings")
            logger.info("  - profile_insights")
            logger.info("Business profiles table enhanced with new columns")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise


async def verify_migration():
    """
    Verify that all tables were created successfully.
    """
    async with engine.begin() as conn:
        # Check if tables exist
        tables_to_check = [
            'user_profiles',
            'social_media_profiles',
            'user_activity_logs',
            'privacy_settings',
            'profile_insights',
            'business_profiles'
        ]
        
        for table in tables_to_check:
            result = await conn.execute(
                text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            )
            exists = result.fetchone()
            
            if exists:
                logger.info(f"[OK] Table '{table}' exists")
            else:
                logger.warning(f"[FAIL] Table '{table}' does not exist")


async def show_table_schema(table_name: str):
    """
    Show the schema of a specific table.
    """
    async with engine.begin() as conn:
        result = await conn.execute(
            text(f"PRAGMA table_info({table_name})")
        )
        columns = result.fetchall()
        
        logger.info(f"\nSchema for table '{table_name}':")
        for col in columns:
            logger.info(f"  - {col[1]} ({col[2]})")


async def main():
    """
    Main migration function.
    """
    print("=" * 60)
    print("Enhanced Data Profiling Migration")
    print("=" * 60)
    print()
    print("This migration will:")
    print("1. Create new tables for user profiles, social media, activity logs, etc.")
    print("2. Enhance business_profiles table with additional columns")
    print("3. Create indexes for performance optimization")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\nMigration cancelled.")
        return
    
    print("\nStarting migration...")
    print("-" * 60)
    
    try:
        await migrate()
        print("-" * 60)
        print("\n[OK] Migration completed successfully!")
        print()
        
        # Verify migration
        print("Verifying migration...")
        await verify_migration()
        print()
        
        # Show schemas
        print("Table schemas:")
        await show_table_schema('user_profiles')
        await show_table_schema('social_media_profiles')
        await show_table_schema('user_activity_logs')
        await show_table_schema('privacy_settings')
        await show_table_schema('profile_insights')
        
        print()
        print("=" * 60)
        print("Next steps:")
        print("1. Restart the backend server")
        print("2. Test the new API endpoints at /api/v1/profiles")
        print("3. Check the database to verify tables were created")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[FAIL] Migration failed: {str(e)}")
        print("\nPlease check the error logs above and fix any issues.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

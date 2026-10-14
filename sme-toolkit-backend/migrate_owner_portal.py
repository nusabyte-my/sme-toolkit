"""Back up and align an existing SQLite business_profiles table without dropping data.
Run from the backend directory: python migrate_owner_portal.py
New databases already get the current schema from app startup.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from sqlalchemy.engine import make_url
from app.config import settings


def migrate():
    url = make_url(settings.database_url)
    if not url.drivername.startswith('sqlite'):
        raise SystemExit('This migration is for SQLite. Apply equivalent nullable columns through your PostgreSQL migration process.')
    path = Path(url.database or '').resolve()
    if not path.is_file():
        raise SystemExit('Database does not exist; start the API to create a fresh schema.')
    columns = {'company_size':'VARCHAR', 'website':'VARCHAR', 'contact_email':'VARCHAR', 'contact_phone':'VARCHAR',
               'country':'VARCHAR', 'city':'VARCHAR', 'meta_json':'JSON'}
    with sqlite3.connect(path) as connection:
        connection.row_factory=sqlite3.Row
        existing={row['name'] for row in connection.execute('PRAGMA table_info(business_profiles)')}
        missing={name:kind for name,kind in columns.items() if name not in existing}
        indexes={row['name'] for row in connection.execute('PRAGMA index_list(sales_transactions)')}
        needs_sales_index='uq_sales_reference' not in indexes
        duplicates=connection.execute('SELECT COUNT(*) FROM (SELECT 1 FROM sales_transactions WHERE external_id IS NOT NULL GROUP BY business_profile_id,platform,external_id HAVING COUNT(*)>1)').fetchone()[0]
        if needs_sales_index and duplicates:
            raise SystemExit('Duplicate sales references exist. Resolve them before migration; no data was changed.')
        if not missing and not needs_sales_index:
            print('Owner schema already aligned; no changes.')
            return
        backup=path.with_name(path.name+'.pre-owner-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.bak')
        with sqlite3.connect(backup) as destination:
            connection.backup(destination)
        with connection:
            for name,kind in missing.items():
                connection.execute(f'ALTER TABLE business_profiles ADD COLUMN {name} {kind}')
            if needs_sales_index:
                connection.execute('CREATE UNIQUE INDEX uq_sales_reference ON sales_transactions (business_profile_id, platform, external_id)')
            for row in connection.execute('SELECT * FROM business_profiles').fetchall():
                data=dict(row)
                meta=json.loads(data.get('meta_json') or '{}')
                for key in ('business_description','products_services','target_market','short_term_goals','brand_voice','revenue_currency','timezone'):
                    value=data.get(key)
                    if value is not None and key not in meta:
                        if key in ('products_services','target_market','short_term_goals') and isinstance(value,str):
                            try:value=json.loads(value)
                            except json.JSONDecodeError:pass
                        meta[key]=value
                if not meta.get('business_description') and data.get('business_context'):
                    meta['business_description']=data['business_context']
                connection.execute('UPDATE business_profiles SET meta_json=?, website=COALESCE(website, ?) WHERE id=?',
                                   (json.dumps(meta),data.get('website_url'),data['id']))
        print(f'Added {len(missing)} nullable columns; preserved existing profiles. Backup: {backup.name}')


if __name__=='__main__':
    migrate()

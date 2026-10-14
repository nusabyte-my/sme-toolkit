"""Align legacy CRM columns without losing lead data. Run from the backend directory."""
from pathlib import Path
from datetime import datetime, timezone
import sqlite3
from sqlalchemy.engine import make_url
from app.config import settings

if __name__=='__main__':
    url=make_url(settings.database_url)
    if not url.drivername.startswith('sqlite'):raise SystemExit('Apply equivalent nullable lead columns through your PostgreSQL migration process.')
    path=Path(url.database or '').resolve()
    if not path.is_file():raise SystemExit('Start the API first to create a new database.')
    columns={'position':'VARCHAR','lead_source':'VARCHAR','last_contacted_at':'DATETIME','next_follow_up_at':'DATETIME','score':'INTEGER','score_factors':'JSON','score_history':'JSON','tags':'JSON','custom_fields':'JSON','meta_json':'JSON'}
    with sqlite3.connect(path) as db:
        present={row[1] for row in db.execute('PRAGMA table_info(leads)')}
        missing={key:value for key,value in columns.items() if key not in present}
        if missing:
            backup=path.with_name(path.name+'.pre-crm-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.bak')
            with sqlite3.connect(backup) as dest:db.backup(dest)
            with db:
                for name,kind in missing.items():db.execute(f'ALTER TABLE leads ADD COLUMN {name} {kind}')
                if 'source' in present:db.execute('UPDATE leads SET lead_source=COALESCE(lead_source,source)')
            print(f'Added {len(missing)} nullable CRM columns; data retained. Backup: {backup.name}')
        else:print('CRM schema already aligned.')

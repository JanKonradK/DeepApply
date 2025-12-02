#!/usr/bin/env python3
"""
CLI tool for running database migrations
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_connection_string():
    """Get PostgreSQL connection string from environment."""
    return os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5433/nyx_venatrix'
    )

def run_migration(conn, sql_file):
    """Run a single migration file."""
    print(f"Running migration: {sql_file}")
    with open(sql_file, 'r') as f:
        sql = f.read()

    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"✅ Completed: {sql_file}")

def main():
    migrations_dir = os.path.join(
        os.path.dirname(__file__),
        'infrastructure/postgres'
    )

    migration_files = sorted([
        f for f in os.listdir(migrations_dir)
        if f.endswith('.sql') and not f.startswith('.')
    ])

    print(f"Found {len(migration_files)} migration files")

    conn_string = get_connection_string()
    print(f"Connecting to database...")

    try:
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        for migration_file in migration_files:
            file_path = os.path.join(migrations_dir, migration_file)
            run_migration(conn, file_path)

        print("\n✅ All migrations completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()

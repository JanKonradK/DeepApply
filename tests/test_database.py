"""
Integration tests for database schema and migrations
"""
import unittest
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class TestDatabaseSchema(unittest.TestCase):
    """Test database schema creation and seeding"""

    @classmethod
    def setUpClass(cls):
        """Connect to test database"""
        conn_string = os.getenv(
            'TEST_DATABASE_URL',
            'postgresql://nyx:nyx_password@localhost:5432/nyx_test'
        )
        try:
            cls.conn = psycopg2.connect(conn_string)
            cls.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except Exception as e:
            raise unittest.SkipTest(f"Cannot connect to test database: {e}")

    @classmethod
    def tearDownClass(cls):
        """Close connection"""
        if hasattr(cls, 'conn'):
            cls.conn.close()

    def test_tables_exist(self):
        """Verify all major tables exist"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]

            required_tables = [
                'users', 'user_profiles', 'resumes', 'applications',
                'application_sessions', 'job_posts', 'companies',
                'application_events', 'qa_checks'
            ]

            for table in required_tables:
                self.assertIn(table, tables, f"Table {table} missing")

    def test_seed_data_loaded(self):
        """Verify seed data is present"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            self.assertGreater(user_count, 0, "No users found in seed data")

            cur.execute("SELECT COUNT(*) FROM companies")
            company_count = cur.fetchone()[0]
            self.assertGreater(company_count, 0, "No companies found in seed data")

    def test_indexes_exist(self):
        """Verify critical indexes exist"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT indexname FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            indexes = [row[0] for row in cur.fetchall()]

            critical_indexes = [
                'idx_applications_user_id',
                'idx_applications_status',
                'idx_app_events_app_id'
            ]

            for idx in critical_indexes:
                self.assertIn(idx, indexes, f"Index {idx} missing")

if __name__ == '__main__':
    unittest.main()

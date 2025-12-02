import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from uuid import uuid4

# Add services to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

# Mock psycopg2 before importing modules that use it
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()

from persistence.src.companies import CompanyRepository
from persistence.src.applications import ApplicationRepository

class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()

        # Mock get_cursor context manager
        self.mock_conn.get_cursor.return_value.__enter__.return_value = self.mock_cursor

        # Mock cursor context manager (for legacy/direct calls if any)
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor

        # Patch get_db to return our mock connection
        self.db_patcher = patch('persistence.src.companies.get_db', return_value=self.mock_conn)
        self.db_patcher.start()

        self.app_db_patcher = patch('persistence.src.applications.get_db', return_value=self.mock_conn)
        self.app_db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()
        self.app_db_patcher.stop()

    def test_company_create(self):
        repo = CompanyRepository()
        self.mock_cursor.fetchone.side_effect = [None, None, {'id': 'new-uuid'}]

        company_id = repo.create_or_update("Test Corp", "test.com")

        self.assertEqual(company_id, 'new-uuid')
        # Verify get_cursor was called
        self.assertTrue(self.mock_conn.get_cursor.called)
        # Verify insert was called
        insert_call = self.mock_cursor.execute.call_args_list[-1]
        self.assertIn("INSERT INTO companies", insert_call[0][0])

    def test_application_mark_started(self):
        repo = ApplicationRepository()
        app_id = uuid4()

        repo.mark_started(app_id)

        # Verify execute_query was called
        self.assertTrue(self.mock_conn.execute_query.called)
        call_args = self.mock_conn.execute_query.call_args[0]
        self.assertIn("UPDATE applications", call_args[0])
        self.assertIn("in_progress", call_args[0])

if __name__ == '__main__':
    unittest.main()

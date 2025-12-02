"""
Test Suite for Advanced Features
Tests Rate Limiting, Policies, and Event Tracking
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from uuid import uuid4, UUID
from datetime import date, datetime, timedelta

# Add services to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

# Mock dependencies
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()


class TestDomainRateLimitRepository(unittest.TestCase):
    """Test domain rate limiting"""

    @patch('persistence.src.domain_limits.get_db')
    def test_record_application(self, mock_get_db):
        """Test recording application stats"""
        from persistence.src.domain_limits import DomainRateLimitRepository

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        repo = DomainRateLimitRepository()

        # Record success
        repo.record_application('example.com', success=True)
        mock_db.execute_query.assert_called_once()

        # Record failure
        mock_db.reset_mock()
        repo.record_application('example.com', success=False)
        mock_db.execute_query.assert_called_once()

    @patch('persistence.src.domain_limits.get_db')
    def test_is_blocked(self, mock_get_db):
        """Test blocking logic"""
        from persistence.src.domain_limits import DomainRateLimitRepository

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        repo = DomainRateLimitRepository()

        # Case 1: Not blocked
        mock_db.execute_query.return_value = [{'is_temporarily_blocked': False}]
        self.assertFalse(repo.is_blocked('example.com'))

        # Case 2: Blocked and active
        future = datetime.now() + timedelta(hours=1)
        mock_db.execute_query.return_value = [{
            'is_temporarily_blocked': True,
            'blocked_until': future
        }]
        self.assertTrue(repo.is_blocked('example.com'))

        # Case 3: Blocked but expired
        past = datetime.now() - timedelta(hours=1)
        mock_db.execute_query.return_value = [{
            'is_temporarily_blocked': True,
            'blocked_until': past
        }]
        # Should trigger unblock
        self.assertFalse(repo.is_blocked('example.com'))


class TestDomainPolicyRepository(unittest.TestCase):
    """Test domain policies"""

    @patch('persistence.src.domain_limits.get_db')
    def test_should_apply(self, mock_get_db):
        """Test policy enforcement"""
        from persistence.src.domain_limits import DomainPolicyRepository

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        repo = DomainPolicyRepository()

        # Case 1: No policy
        mock_db.execute_query.return_value = []
        should_apply, reason = repo.should_apply_to_domain('example.com', 0)
        self.assertTrue(should_apply)

        # Case 2: Avoid if possible
        mock_db.execute_query.return_value = [{'avoid_if_possible': True}]
        should_apply, reason = repo.should_apply_to_domain('example.com', 0)
        self.assertFalse(should_apply)
        self.assertIn("avoid", reason)

        # Case 3: Daily limit reached
        mock_db.execute_query.return_value = [{'max_applications_per_day': 5}]
        should_apply, reason = repo.should_apply_to_domain('example.com', 5)
        self.assertFalse(should_apply)
        self.assertIn("limit", reason)

        # Case 4: Daily limit not reached
        should_apply, reason = repo.should_apply_to_domain('example.com', 4)
        self.assertTrue(should_apply)


class TestCaptchaEventsRepository(unittest.TestCase):
    """Test CAPTCHA event tracking"""

    @patch('persistence.src.captcha_events.get_db')
    def test_log_captcha_event(self, mock_get_db):
        """Test logging CAPTCHA event"""
        from persistence.src.captcha_events import CaptchaEventsRepository

        mock_db = MagicMock()
        event_id = uuid4()
        mock_db.execute_query.return_value = [{'id': str(event_id)}]
        mock_get_db.return_value = mock_db

        repo = CaptchaEventsRepository()

        result = repo.log_captcha_event(
            application_id=uuid4(),
            provider='recaptcha_v2',
            status='solved'
        )

        self.assertEqual(str(result), str(event_id))
        mock_db.execute_query.assert_called_once()


class TestTwoFactorEventsRepository(unittest.TestCase):
    """Test 2FA event tracking"""

    @patch('persistence.src.captcha_events.get_db')
    def test_log_2fa_request(self, mock_get_db):
        """Test logging 2FA request"""
        from persistence.src.captcha_events import TwoFactorEventsRepository

        mock_db = MagicMock()
        event_id = uuid4()
        mock_db.execute_query.return_value = [{'id': str(event_id)}]
        mock_get_db.return_value = mock_db

        repo = TwoFactorEventsRepository()

        result = repo.log_2fa_request(
            application_id=uuid4(),
            method='sms'
        )

        self.assertEqual(str(result), str(event_id))
        mock_db.execute_query.assert_called_once()


if __name__ == '__main__':
    unittest.main()

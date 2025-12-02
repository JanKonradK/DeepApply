"""
Test Suite for Nyx Venatrix Services
Tests SessionManager, CaptchaSolver, TelegramNotifier, and persistence
"""
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
from uuid import uuid4, UUID
from datetime import datetime

# Add services to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

# Mock heavy dependencies
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.error'] = MagicMock()
sys.modules['browser_use'] = MagicMock()
sys.modules['browser_use.llm'] = MagicMock()
sys.modules['browser_use.llm.openai'] = MagicMock()
sys.modules['browser_use.llm.openai.chat'] = MagicMock()


class TestSessionManager(unittest.TestCase):
    """Test SessionManager service"""

    @patch('agent.src.session_manager.SessionRepository')
    @patch('agent.src.session_manager.ApplicationRepository')
    @patch('agent.src.session_manager.EventRepository')
    def test_create_session(self, mock_event_repo, mock_app_repo, mock_session_repo):
        """Test session creation"""
        from agent.src.session_manager import SessionManager

        # Setup mocks
        mock_session_repo_instance = MagicMock()
        mock_session_repo.return_value = mock_session_repo_instance

        session_id = uuid4()
        mock_session_repo_instance.create_session.return_value = session_id

        # Create session manager
        manager = SessionManager()

        # Create session
        user_id = uuid4()
        result = manager.create_session(
            user_id=user_id,
            session_name="Test Session",
            max_applications=50
        )

        # Verify
        self.assertEqual(result, session_id)
        mock_session_repo_instance.create_session.assert_called_once()
        mock_session_repo_instance.add_session_event.assert_called_once()


class TestCaptchaSolver(unittest.TestCase):
    """Test CAPTCHA solver"""

    @patch('agent.src.captcha.solver.requests')
    def test_solve_recaptcha_v2(self, mock_requests):
        """Test reCAPTCHA v2 solving"""
        from agent.src.captcha.solver import CaptchaSolver

        # Setup mock responses
        submit_response = MagicMock()
        submit_response.json.return_value = {'status': 1, 'request': 'captcha_id_123'}

        solution_response = MagicMock()
        solution_response.json.return_value = {'status': 1, 'request': 'solution_token_xyz'}

        mock_requests.post.return_value = submit_response
        mock_requests.get.return_value = solution_response

        # Create solver
        solver = CaptchaSolver(api_key='test_key')

        # Solve CAPTCHA
        result = solver.solve_recaptcha_v2(
            site_key='test_site_key',
            page_url='https://example.com'
        )

        # Verify
        self.assertEqual(result, 'solution_token_xyz')
        mock_requests.post.assert_called_once()

    def test_solver_without_api_key(self):
        """Test solver fails gracefully without API key"""
        from agent.src.captcha.solver import CaptchaSolver

        solver = CaptchaSolver(api_key=None)
        result = solver.solve_recaptcha_v2('key', 'url')

        self.assertIsNone(result)


class TestTelegramNotifier(unittest.TestCase):
    """Test Telegram notifications"""

    @patch('agent.src.notifications.telegram_notifier.Bot')
    def test_send_2fa_request(self, mock_bot):
        """Test 2FA notification"""
        from agent.src.notifications.telegram_notifier import TelegramNotifier

        # Setup mock
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance

        # Create notifier
        notifier = TelegramNotifier(bot_token='test_token', chat_id='test_chat')

        # Send notification
        result = notifier.send_2fa_request(
            application_id=uuid4(),
            job_title="Software Engineer",
            company_name="Tech Corp",
            method="sms"
        )

        # Verify
        self.assertTrue(result)
        mock_bot_instance.send_message.assert_called_once()


class TestModelUsageRepository(unittest.TestCase):
    """Test model usage tracking"""

    @patch('persistence.src.model_usage.get_db')
    def test_log_model_call(self, mock_get_db):
        """Test logging a model call"""
        from persistence.src.model_usage import ModelUsageRepository

        # Setup mock
        mock_db = MagicMock()
        mock_db.execute_query.return_value = [{'id': str(uuid4())}]
        mock_get_db.return_value = mock_db

        repo = ModelUsageRepository()

        # Log call
        result = repo.log_model_call(
            model_name='grok-beta',
            call_type='chat_completion',
            tokens_input=100,
            tokens_output=50,
            cost_estimated=0.001,
            purpose='cover_letter'
        )

        # Verify - result is a string UUID
        self.assertIsInstance(UUID(result), UUID)
        mock_db.execute_query.assert_called_once()


class TestQARepository(unittest.TestCase):
    """Test QA repository"""

    @patch('persistence.src.qa.get_db')
    def test_create_qa_check(self, mock_get_db):
        """Test creating QA check"""
        from persistence.src.qa import QARepository

        # Setup mock
        mock_db = MagicMock()
        qa_check_id = uuid4()
        mock_db.execute_query.return_value = [{'id': str(qa_check_id)}]
        mock_get_db.return_value = mock_db

        repo = QARepository()

        # Create check
        result = repo.create_qa_check(
            application_id=uuid4(),
            qa_type='hallucination_check',
            status='passed'
        )

        # Verify - compare as strings
        self.assertEqual(str(result), str(qa_check_id))
        mock_db.execute_query.assert_called_once()


class TestEnhancedFormFiller(unittest.TestCase):
    """Test EnhancedFormFiller integration"""

    @patch('agent.src.agents.enhanced_form_filler.yaml')
    @patch('builtins.open')
    def test_form_filler_initialization(self, mock_open, mock_yaml):
        """Test form filler initializes with CAPTCHA and Telegram"""
        from agent.src.agents.enhanced_form_filler import EnhancedFormFiller

        # Setup mocks
        mock_yaml.safe_load.return_value = {'randomization': {}}
        mock_answer_gen = MagicMock()
        mock_captcha = MagicMock()
        mock_telegram = MagicMock()

        # Create filler
        filler = EnhancedFormFiller(
            answer_generator=mock_answer_gen,
            captcha_solver=mock_captcha,
            telegram_notifier=mock_telegram
        )

        # Verify
        self.assertIsNotNone(filler.captcha_solver)
        self.assertIsNotNone(filler.telegram_notifier)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCaptchaSolver))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramNotifier))
    suite.addTests(loader.loadTestsFromTestCase(TestModelUsageRepository))
    suite.addTests(loader.loadTestsFromTestCase(TestQARepository))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedFormFiller))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

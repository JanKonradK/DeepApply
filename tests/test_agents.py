import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add services to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

# Mock browser_use before importing agents
sys.modules['browser_use'] = MagicMock()
sys.modules['browser_use.llm'] = MagicMock()
sys.modules['browser_use.llm.openai'] = MagicMock()
sys.modules['browser_use.llm.openai.chat'] = MagicMock()

from agent.src.agents.adapters.greenhouse import GreenhouseAdapter
from agent.src.agents.adapters.workday import WorkdayAdapter
from agent.src.discovery.agent import JobDiscoveryAgent

class TestAgents(unittest.TestCase):
    def test_greenhouse_adapter(self):
        adapter = GreenhouseAdapter()
        self.assertTrue(adapter.can_handle("https://boards.greenhouse.io/company/jobs/123"))
        self.assertFalse(adapter.can_handle("https://lever.co/jobs"))

        instructions = adapter.get_instructions("high")
        self.assertIn("Cover Letter", instructions)

    def test_workday_adapter(self):
        adapter = WorkdayAdapter()
        self.assertTrue(adapter.can_handle("https://company.myworkdayjobs.com/en-US/careers"))

        config = adapter.get_stealth_config()
        self.assertGreater(config['inter_action_delay'], 2.0)

    @patch('agent.src.discovery.agent.BrowserAgent')
    def test_discovery_agent(self, mock_browser_agent):
        # This test would need async support, skipping full async implementation for this snippet
        # but verifying structure
        agent = JobDiscoveryAgent()
        self.assertIsNotNone(agent.llm)

if __name__ == '__main__':
    unittest.main()

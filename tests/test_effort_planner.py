"""
Comprehensive test suite for effort planning
Tests all decision logic, policy enforcement, and edge cases
"""
import unittest
from uuid import uuid4
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

from agent.src.planning.effort_planner import EffortPlanner


class TestEffortPlanner(unittest.TestCase):
    """Test effort planning decisions"""

    def setUp(self):
        """Initialize effort planner with test policy"""
        self.planner = EffortPlanner()

    def test_high_match_score_upgrades(self):
        """Test that high match scores trigger upgrades"""
        # High match (>0.75) should upgrade low to medium
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='low',
            match_score=0.80,
            company_tier='normal'
        )

        self.assertEqual(effort, 'medium')
        self.assertIn('Strong match', reason)
        self.assertFalse(skip)

    def test_top_tier_company_upgrades(self):
        """Test that top-tier companies trigger upgrades"""
        # Top tier should upgrade low to medium
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='low',
            match_score=0.65,
            company_tier='top'
        )

        self.assertEqual(effort, 'medium')
        self.assertIn('top', reason.lower())
        self.assertFalse(skip)

    def test_low_match_score_downgrades(self):
        """Test that low match scores trigger downgrades"""
        # Low match (<0.50) should downgrade medium to low
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='medium',
            match_score=0.40,
            company_tier='normal'
        )

        self.assertEqual(effort, 'low')
        self.assertIn('Low match', reason)
        self.assertFalse(skip)

    def test_avoid_company_skip(self):
        """Test that 'avoid' tier companies are skipped"""
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='medium',
            match_score=0.70,
            company_tier='avoid'
        )

        self.assertTrue(skip)
        self.assertIn('avoid', reason.lower())

    def test_very_low_match_skip(self):
        """Test that very low match scores trigger skip"""
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='medium',
            match_score=0.25,
            company_tier='normal'
        )

        self.assertTrue(skip)
        self.assertIn('too low', reason.lower())

    def test_top_tier_high_match_upgrades_to_high(self):
        """Test that top tier + good match upgrades to high"""
        # Top tier + good match (>=0.60) should upgrade medium to high
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='medium',
            match_score=0.70,
            company_tier='top'
        )

        self.assertEqual(effort, 'high')
        self.assertFalse(skip)

    def test_user_hint_respected_when_valid(self):
        """Test that user hint is respected when match score is acceptable"""
        # Medium hint with acceptable match should stay medium
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='medium',
            match_score=0.65,
            company_tier='normal'
        )

        self.assertEqual(effort, 'medium')
        self.assertFalse(skip)

    def test_qa_requirements_for_high_effort(self):
        """Test that high effort requires QA"""
        requires_qa, qa_type = self.planner.requires_qa('high', 'normal')

        self.assertTrue(requires_qa)
        self.assertEqual(qa_type, 'hallucination_check')

    def test_qa_requirements_for_top_tier_medium(self):
        """Test that top tier medium effort requires QA"""
        requires_qa, qa_type = self.planner.requires_qa('medium', 'top')

        self.assertTrue(requires_qa)
        self.assertEqual(qa_type, 'consistency_check')

    def test_no_qa_for_low_effort(self):
        """Test that low effort doesn't require QA"""
        requires_qa, qa_type = self.planner.requires_qa('low', 'normal')

        self.assertFalse(requires_qa)
        self.assertIsNone(qa_type)

    def test_edge_case_exact_threshold(self):
        """Test behavior at exact threshold values"""
        # At exactly 0.75 threshold
        effort, reason, skip = self.planner.decide_effort_level(
            user_hint='low',
            match_score=0.75,
            company_tier='normal'
        )

        # Should upgrade at >= threshold
        self.assertEqual(effort, 'medium')
        self.assertFalse(skip)


if __name__ == '__main__':
    unittest.main()

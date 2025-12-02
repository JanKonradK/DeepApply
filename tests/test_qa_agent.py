"""
Test suite for QA Agent
"""
import unittest
from uuid import uuid4
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

from agent.src.qa.qa_agent import QAAgent


class TestQAAgent(unittest.TestCase):
    """Test QA validation logic"""

    def setUp(self):
        """Set up QA agent with mock profile truth"""
        self.profile_truth = {
            'skills_true': ['Python', 'Ray', 'MLflow', 'Docker'],
            'skills_false': ['Java', 'C++', 'PHP'],
            'max_years_experience': 5
        }
        self.qa = QAAgent(self.profile_truth)

    def test_detect_disallowed_skill(self):
        """Test detection of disallowed skills"""
        answers = [
            {
                'field_label_raw': 'Programming Languages',
                'value_filled': 'I am proficient in Python, Java, and Docker'
            }
        ]

        result = self.qa.validate_answers(answers, '')

        self.assertEqual(result['status'], 'issues_found')
        self.assertGreater(result['issues_count'], 0)

        # Check that Java was flagged
        java_issues = [i for i in result['issues'] if i.get('skill') == 'Java']
        self.assertGreater(len(java_issues), 0)

    def test_detect_experience_inflation(self):
        """Test detection of inflated experience"""
        answers = [
            {
                'field_label_raw': 'Years of Experience',
                'value_filled': 'I have 10 years of experience in Python'
            }
        ]

        result = self.qa.validate_answers(answers, '')

        # Should flag 10 years when max is 5
        inflation_issues = [i for i in result['issues'] if i.get('type') == 'experience_inflation']
        self.assertGreater(len(inflation_issues), 0)

    def test_pass_clean_answers(self):
        """Test that clean answers pass validation"""
        answers = [
            {
                'field_label_raw': 'Skills',
                'value_filled': 'Python, Ray, MLflow'
            },
            {
                'field_label_raw': 'Experience',
                'value_filled': 'I have 5 years of experience'
            }
        ]

        result = self.qa.validate_answers(answers, '')

        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['issues_count'], 0)

    def test_cover_letter_validation(self):
        """Test cover letter validation"""
        cover_letter = "I am an expert in Python, Ray, and Java development..."

        result = self.qa.validate_answers([], '', cover_letter=cover_letter)

        # Should flag Java in cover letter
        self.assertEqual(result['status'], 'issues_found')
        cl_issues = [i for i in result['issues'] if 'cover_letter' in i.get('type', '')]
        self.assertGreater(len(cl_issues), 0)


if __name__ == '__main__':
    unittest.main()

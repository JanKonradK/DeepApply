"""
Example: Testing Profile Matcher and Effort Planner

This script demonstrates the Phase 2-3 functionality:
- Profile embedding and job matching
- Effort level decision based on policy
"""

import os
import sys

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.matching.profile_matcher import ProfileMatcher
from src.planning.effort_planner import EffortPlanner
from src.job_ingestion import JobIngestionService


def test_profile_matching():
    """Test profile matcher with sample data"""
    print("\n" + "="*60)
    print("Testing Profile Matcher")
    print("="*60)

    # Sample profile
    profile_text = """
    Senior AI/ML Engineer with 3+ years of experience in:
    - Python, FastAPI, PyTorch
    - LangChain, LangGraph, RAG systems
    - OpenAI API, Anthropic Claude
    - MLflow, PostgreSQL, Docker
    - Browser automation with Playwright

    Education: MSc Computer Science (Machine Learning)
    Languages: English (C2), Polish (C2), German (B2)
    """

    # Sample job descriptions
    jobs = [
        {
            'title': 'Senior ML Engineer',
            'description': """
            We're looking for a Senior ML Engineer with strong Python and PyTorch experience.
            You'll build LLM applications using LangChain and work with vector databases.
            Experience with FastAPI and PostgreSQL required.
            """
        },
        {
            'title': 'Frontend Developer',
            'description': """
            React developer needed for building modern web applications.
            Experience with TypeScript, Redux, and responsive design is essential.
            No backend experience needed.
            """
        },
        {
            'title': 'Data Analyst',
            'description': """
            Looking for a data analyst with SQL and Excel skills.
            Experience with Tableau and business intelligence tools preferred.
            """
        }
    ]

    # Initialize matcher
    matcher = ProfileMatcher()
    print("\n📚 Loading profile...")
    matcher.load_profile(profile_text)
    print(f"✅ Profile loaded ({len(profile_text)} chars)")

    # Test matching
    print("\n🎯 Computing match scores:\n")
    for job in jobs:
        score = matcher.compute_match_score(job['description'])
        print(f"  {job['title']:30s} → Match: {score:.2%}")

    print("\n✅ Profile matching test complete!")
    return matcher


def test_effort_planning(matcher):
    """Test effort planner with various scenarios"""
    print("\n" + "="*60)
    print("Testing Effort Planner")
    print("="*60)

    # Initialize planner
    planner = EffortPlanner()
    print("\n📋 Policy loaded")
    print(f"   High match threshold: {planner.thresholds.get('high_match')}")
    print(f"   Medium match threshold: {planner.thresholds.get('medium_match')}")
    print(f"   Low match threshold: {planner.thresholds.get('low_match')}")

    # Test scenarios
    scenarios = [
        {'hint': 'low', 'score': 0.85, 'tier': 'normal', 'desc': 'Strong match, normal company'},
        {'hint': 'low', 'score': 0.70, 'tier': 'top', 'desc': 'Good match, top company'},
        {'hint': 'medium', 'score': 0.45, 'tier': 'normal', 'desc': 'Weak match'},
        {'hint': 'high', 'score': 0.25, 'tier': 'normal', 'desc': 'Very weak match, high effort'},
        {'hint': 'medium', 'score': 0.60, 'tier': 'avoid', 'desc': 'Avoid tier company'},
    ]

    print("\n🔧 Testing effort decisions:\n")
    for scenario in scenarios:
        effort, reason, skip = planner.decide_effort_level(
            scenario['hint'],
            scenario['score'],
            scenario['tier']
        )

        status = "⏭️  SKIP" if skip else f"✅ {effort.upper()}"
        print(f"  {scenario['desc']:40s}")
        print(f"    Hint: {scenario['hint']}, Score: {scenario['score']:.2f}, Tier: {scenario['tier']}")
        print(f"    → {status}: {reason}\n")

    print("✅ Effort planning test complete!")
    return planner


def test_full_pipeline(matcher, planner):
    """Test full job ingestion pipeline"""
    print("\n" + "="*60)
    print("Testing Full Job Ingestion Pipeline")
    print("="*60)

    # Initialize service
    service = JobIngestionService(matcher, planner)

    # Sample job
    job_url = "https://careers.example.com/ml-engineer"
    job_metadata = {
        'title': 'ML Engineer',
        'company': 'Example Corp',
        'description_clean': """
        We need an ML Engineer with Python, PyTorch, and LangChain experience.
        You'll build RAG systems and LLM applications using FastAPI and PostgreSQL.
        Experience with MLflow and Docker is a plus.
        """
    }

    print(f"\n🔗 Processing job: {job_url}")
    print(f"   Company tier: top")
    print(f"   User hint: medium\n")

    result = service.process_job_url(
        url=job_url,
        user_effort_hint='medium',
        company_tier='top',
        job_metadata=job_metadata
    )

    print("📊 Result:")
    print(f"   Status: {result['status']}")
    if result['status'] == 'processed':
        print(f"   Match score: {result['match_score']:.2%}")
        print(f"   Effort level: {result['effort_level']}")
        print(f"   Reason: {result['effort_reason']}")
        print(f"   Requires QA: {result['requires_qa']}")
        if result['requires_qa']:
            print(f"   QA type: {result['qa_type']}")

    print("\n✅ Full pipeline test complete!")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Nyx Venatrix - Phase 2-3 Integration Test")
    print("="*60)

    # Test each component
    matcher = test_profile_matching()
    planner = test_effort_planning(matcher)
    test_full_pipeline(matcher, planner)

    print("\n" + "="*60)
    print("✨ All tests complete!")
    print("="*60 + "\n")

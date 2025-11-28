import asyncio
from services.agent.src.orchestrator import Orchestrator

async def test_pipeline():
    orchestrator = Orchestrator()

    # Mock URL and Profile
    url = "https://example.com/job-posting"
    profile = "John Doe, Python Developer, 5 years experience..."

    print("\n--- Testing LOW Effort ---")
    await orchestrator.run_pipeline(url, effort_level="LOW", user_profile=profile)

    print("\n--- Testing MEDIUM Effort ---")
    await orchestrator.run_pipeline(url, effort_level="MEDIUM", user_profile=profile)

    print("\n--- Testing HIGH Effort ---")
    await orchestrator.run_pipeline(url, effort_level="HIGH", user_profile=profile)

if __name__ == "__main__":
    asyncio.run(test_pipeline())

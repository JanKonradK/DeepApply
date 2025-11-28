import asyncio
from typing import Dict, Any
from .agents.scraper import ScraperAgent
from .agents.writer import CVTailorAgent, CoverLetterAgent
from .agents.form_filler import FormFillerAgent
from .agents.reviewer import ReviewerAgent

class Orchestrator:
    def __init__(self):
        self.scraper = ScraperAgent()
        self.cv_tailor = CVTailorAgent()
        self.cl_writer = CoverLetterAgent()
        self.form_filler = FormFillerAgent()
        self.reviewer = ReviewerAgent()

    async def run_pipeline(self, url: str, effort_level: str = "MEDIUM", user_profile: str = ""):
        print(f"🚀 Orchestrator: Starting {effort_level} effort application for {url}")

        # Step 1: Scrape (Sequential)
        job_data = await self.scraper.run({"url": url})
        if "error" in job_data:
            return {"status": "failed", "reason": "Scraping failed"}

        # Step 2: Parallel Generation
        print("⚡ Orchestrator: Parallel generation starting...")
        tasks = []

        # Always write CL for Medium/High
        if effort_level in ["MEDIUM", "HIGH"]:
            tasks.append(self.cl_writer.run({"job_data": job_data, "user_profile": user_profile}))

        # Only tailor CV for High
        if effort_level == "HIGH":
            tasks.append(self.cv_tailor.run({"job_data": job_data, "current_cv": user_profile})) # Mocking CV as profile for now

        artifacts = await asyncio.gather(*tasks)
        print(f"✅ Orchestrator: Generated {len(artifacts)} artifacts.")

        # Step 3: Form Filling
        fill_result = await self.form_filler.run({
            "url": url,
            "user_profile": user_profile,
            "artifacts": artifacts
        })

        # Step 4: Review (High Effort Only)
        if effort_level == "HIGH":
            review = await self.reviewer.run({"form_summary": fill_result.get("summary")})
            if not review.get("decision", "").lower().count("true"): # Simple check
                print("❌ Reviewer rejected. Manual intervention needed.")
                return {"status": "review_failed", "feedback": review}

        return {"status": "success", "data": job_data, "artifacts": artifacts, "form": fill_result}

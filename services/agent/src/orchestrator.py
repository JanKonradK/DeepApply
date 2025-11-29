import asyncio
from typing import Dict, Any
from .agents.scraper import ScraperAgent
from .agents.writer import CVTailorAgent, CoverLetterAgent
from .agents.form_filler import FormFillerAgent
from .agents.reviewer import ReviewerAgent
from .utils.salary_oracle import SalaryOracle

class Orchestrator:
    def __init__(self):
        self.scraper = ScraperAgent()
        self.cv_tailor = CVTailorAgent()
        self.cl_writer = CoverLetterAgent()
        self.form_filler = FormFillerAgent()
        self.reviewer = ReviewerAgent()
        self.salary_oracle = SalaryOracle()

    async def run_pipeline(self, url: str, effort_level: str = "MEDIUM", user_profile: str = ""):
        print(f"🚀 Orchestrator: Starting {effort_level} effort application for {url}")

        # Step 1: Scrape job data
        job_data = await self.scraper.run({"url": url})
        if "error" in job_data:
            return {"status": "failed", "reason": "Scraping failed", "error": job_data}

        # Step 1.5: Estimate salary (informational)
        salary_estimate = None
        try:
            job_title = job_data.get("title", "Software Engineer")
            location = job_data.get("location", "San Francisco")
            salary_estimate = self.salary_oracle.estimate_salary(job_title, location)
            if salary_estimate:
                print(f"💰 Salary estimate: ${salary_estimate['medianSalary']:,} "
                      f"(${salary_estimate['minSalary']:,} - ${salary_estimate['maxSalary']:,})")
        except Exception as e:
            print(f"⚠️ Salary estimation skipped: {e}")

        # Step 2: Parallel content generation
        print("⚡ Orchestrator: Parallel generation starting...")
        tasks = []

        # Always write cover letter for Medium/High
        if effort_level in ["MEDIUM", "HIGH"]:
            tasks.append(self.cl_writer.run({
                "job_data": job_data,
                "user_profile": user_profile,
                "salary_estimate": salary_estimate  # Include salary context
            }))

        # Only tailor CV for High effort
        if effort_level == "HIGH":
            tasks.append(self.cv_tailor.run({
                "job_data": job_data,
                "current_cv": user_profile
            }))

        artifacts = await asyncio.gather(*tasks) if tasks else []
        print(f"✅ Orchestrator: Generated {len(artifacts)} artifacts")

        # Step 3: Form filling
        fill_result = await self.form_filler.run({
            "url": url,
            "user_profile": user_profile,
            "artifacts": artifacts
        })

        # Step 4: Review (High effort only)
        if effort_level == "HIGH" and fill_result.get("status") == "filled":
            review = await self.reviewer.run({"form_summary": fill_result.get("summary")})
            if not review.get("decision", "").lower().count("approve"):
                print("❌ Reviewer rejected. Manual intervention needed.")
                return {
                    "status": "review_failed",
                    "feedback": review,
                    "data": job_data,
                    "salary_estimate": salary_estimate
                }

        return {
            "status": fill_result.get("status", "unknown"),
            "data": job_data,
            "artifacts": artifacts,
            "form": fill_result,
            "salary_estimate": salary_estimate,
            "effort_level": effort_level
        }

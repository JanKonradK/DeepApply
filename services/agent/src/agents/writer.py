from .base import BaseAgent
from typing import Dict, Any

class CoverLetterAgent(BaseAgent):
    async def run(self, inputs: Dict[str, Any]) -> str:
        job_data = inputs.get("job_data")
        user_profile = inputs.get("user_profile")
        print(f"✍️ CoverLetterAgent: Drafting for {job_data.get('role_title')}...")

        prompt = f"""
        Write a compelling cover letter for the role of {job_data.get('role_title')} at {job_data.get('company_name')}.

        JOB SUMMARY:
        {job_data.get('description_summary')}

        CANDIDATE PROFILE:
        {user_profile}

        INSTRUCTIONS:
        - Use a professional but enthusiastic tone.
        - Highlight 2-3 key matches between the candidate's skills and the job requirements.
        - Keep it under 450 words.
        - Return ONLY the body text (no headers/dates).
        """

        response = await self.llm.ainvoke(prompt)
        return response.content

class CVTailorAgent(BaseAgent):
    async def run(self, inputs: Dict[str, Any]) -> str:
        job_data = inputs.get("job_data")
        current_cv = inputs.get("current_cv")
        print(f"✂️ CVTailorAgent: Tailoring CV for {job_data.get('role_title')}...")

        prompt = f"""
        You are an expert CV writer. Analyze the job description and the candidate's current CV.
        Identify 3 specific sections (e.g., Summary, Skills, specific Experience bullets) that should be modified to better match the job.

        JOB REQUIREMENTS:
        {job_data.get('key_skills')}

        CURRENT CV CONTENT:
        {current_cv[:3000]}... (truncated)

        OUTPUT FORMAT:
        Return a JSON list of edits:
        [
            {{"section": "Summary", "original": "...", "new": "..."}},
            {{"section": "Skills", "original": "...", "new": "..."}}
        ]
        """

        response = await self.llm.ainvoke(prompt)
        return response.content

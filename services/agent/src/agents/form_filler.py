from .base import BaseAgent
from typing import Dict, Any
from browser_use import Agent

class FormFillerAgent(BaseAgent):
    """
    Fills the application form using the generated artifacts.
    """
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        url = inputs.get("url")
        user_profile = inputs.get("user_profile")
        artifacts = inputs.get("artifacts", [])

        # Extract CL/CV from artifacts if available
        # This logic would be more robust in a real implementation
        cover_letter = artifacts[0] if len(artifacts) > 0 else ""

        print(f"🤖 FormFillerAgent: Filling form at {url}...")

        task = f"""
        Navigate to {url}.
        Fill out the application form.

        USER CONTEXT:
        {user_profile}

        COVER LETTER CONTENT (Paste this if asked):
        {cover_letter}

        INSTRUCTIONS:
        - Fill all required fields.
        - Upload CV if requested (use placeholder path '/app/cv.pdf').
        - **OPEN-ENDED QUESTIONS**: For any text area asking "Why us?", "Cover Letter", or "Additional Info":
          - You MUST write a detailed response.
          - If there is a character limit (e.g., 500 chars), use ~90% of it (e.g., 450 chars).
          - Do NOT be brief. Quality and depth are the priority.
        - If you encounter a 'Review' page, STOP and return the current state.
        - DO NOT SUBMIT unless explicitly told to (which we aren't doing yet).
        """

        agent = Agent(task=task, llm=self.llm)
        history = await agent.run()
        result = history.final_result()

        return {"status": "filled", "summary": result}

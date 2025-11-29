from .base import BaseAgent
from typing import Dict, Any
from browser_use import Agent
from ..utils.captcha_solver import CaptchaSolver
from ..utils.telegram_notifier import TelegramNotifier
import os

# Add parent directory to path for utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.captcha_solver import CaptchaSolver
from utils.telegram_notifier import TelegramNotifier

class FormFillerAgent(BaseAgent):
    """
    Fills the application form using the generated artifacts.
    Handles CAPTCHAs and notifies user on failures.
    """
    def __init__(self):
        super().__init__()
        self.captcha_solver = CaptchaSolver()
        self.telegram = TelegramNotifier()

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        url = inputs.get("url")
        user_profile = inputs.get("user_profile")
        artifacts = inputs.get("artifacts", [])

        # Extract CL/CV from artifacts if available
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
        - **CAPTCHA HANDLING**:
          - If you encounter a CAPTCHA (reCAPTCHA, hCaptcha, or image challenge), PAUSE.
          - Take a screenshot and return the element details.
        - If you encounter a 'Review' page, STOP and return the current state.
        - DO NOT SUBMIT unless explicitly told to (which we aren't doing yet).
        """

        agent = Agent(task=task, llm=self.llm)
            if reply and reply.lower() in ["retry", "fixed"]:
                 return {"status": "retrying", "summary": "User fixed issue"}
            else:
                 return {"status": "failed", "summary": "Human intervention failed/timed out"}

        return {"status": "filled", "summary": result}

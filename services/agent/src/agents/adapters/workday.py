from typing import Dict, Any
from .base import ATSAdapter

class WorkdayAdapter(ATSAdapter):
    """
    Adapter for Workday ATS.
    Workday is complex, often requiring account creation/login and multi-step wizards.
    """

    def can_handle(self, url: str) -> bool:
        return "myworkdayjobs.com" in url or "workday" in url

    def get_instructions(self, effort_level: str) -> str:
        return """
        WORKDAY SPECIFIC INSTRUCTIONS:
        - Workday requires an account. If not logged in, look for "Create Account" or "Sign In".
        - If "Quick Apply" is available, use it.
        - Navigation is often "Next" or "Save and Continue".
        - Parsing resumes often fails, so double-check pre-filled fields.
        - Handle the "My Experience" section carefully.
        """

    def get_stealth_config(self) -> Dict[str, Any]:
        return {
            "inter_action_delay": 2.5, # Workday is slower and more sensitive
            "typing_delay_multiplier": 1.5
        }

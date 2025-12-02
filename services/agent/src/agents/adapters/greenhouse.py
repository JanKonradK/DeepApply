from typing import Dict, Any
from .base import ATSAdapter

class GreenhouseAdapter(ATSAdapter):
    """
    Adapter for Greenhouse ATS.
    """

    def can_handle(self, url: str) -> bool:
        return "greenhouse.io" in url or "gh_jid" in url

    def get_instructions(self, effort_level: str) -> str:
        base_instructions = """
        GREENHOUSE SPECIFIC INSTRUCTIONS:
        - The form is usually single-page.
        - Look for "Apply for this Job" button if not immediately visible.
        - "Attach" buttons for Resume/CV might be hidden file inputs.
        - Required fields often have an asterisk *.
        """

        if effort_level == "high":
            base_instructions += "\n- Fill out the 'Cover Letter' section if available."

        return base_instructions

    def get_stealth_config(self) -> Dict[str, Any]:
        return {
            "inter_action_delay": 1.5,
            "typing_delay_multiplier": 1.2
        }

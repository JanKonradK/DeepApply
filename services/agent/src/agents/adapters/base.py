from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ATSAdapter(ABC):
    """
    Abstract base class for ATS-specific adapters.
    Adapters handle the nuances of different job boards (Workday, Greenhouse, etc.)
    """

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this adapter can handle the given URL."""
        pass

    @abstractmethod
    def get_instructions(self, effort_level: str) -> str:
        """Get specific instructions for the browser agent for this ATS."""
        pass

    @abstractmethod
    def get_stealth_config(self) -> Dict[str, Any]:
        """Get stealth configuration specific to this ATS."""
        pass

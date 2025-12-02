"""
Browser Configuration Utility
Configures browser-use to work in different environments (WSL, Docker, IDE)
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class BrowserConfig:
    """
    Manages browser configuration for different environments.

    Supports:
    - CDP connection to existing Chrome
    - Local browser launch
    - Headless mode for CI/CD
    """

    def __init__(self):
        self.mode = os.getenv('BROWSER_MODE', 'auto')
        self.cdp_url = os.getenv('CHROME_CDP_URL')
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'

    def get_playwright_config(self) -> Dict[str, Any]:
        """
        Get playwright browser configuration.

        Returns:
            Dict with browser configuration
        """
        config = {
            'headless': self.headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
            ]
        }

        # Add additional args for stealth
        if not self.headless:
            config['args'].extend([
                '--start-maximized',
                '--disable-infobars',
            ])

        return config

    def should_use_cdp(self) -> bool:
        """Check if CDP connection should be used"""
        return self.cdp_url is not None and self.mode in ['cdp', 'auto']

    def get_cdp_url(self) -> Optional[str]:
        """Get CDP endpoint URL"""
        return self.cdp_url

    def detect_environment(self) -> str:
        """
        Detect the current environment.

        Returns:
            'wsl', 'docker', 'linux', 'windows', or 'unknown'
        """
        # Check for WSL
        if Path('/proc/version').exists():
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    return 'wsl'

        # Check for Docker
        if Path('/.dockerenv').exists():
            return 'docker'

        # Check OS
        if os.name == 'nt':
            return 'windows'
        elif os.name == 'posix':
            return 'linux'

        return 'unknown'

    def recommend_configuration(self) -> Dict[str, Any]:
        """
        Recommend browser configuration based on environment.

        Returns:
            Dict with recommended settings
        """
        env = self.detect_environment()

        if env == 'wsl':
            return {
                'mode': 'cdp',
                'headless': False,
                'note': 'WSL detected - CDP connection recommended. Set CHROME_CDP_URL or use Docker.',
                'alternative': 'Use docker-compose for browser automation'
            }
        elif env == 'docker':
            return {
                'mode': 'headless',
                'headless': True,
                'note': 'Docker detected - headless mode recommended'
            }
        else:
            return {
                'mode': 'local',
                'headless': self.headless,
                'note': f'{env.upper()} detected - local browser launch OK'
            }

    def print_config_info(self):
        """Print current configuration"""
        env = self.detect_environment()
        recommendation = self.recommend_configuration()

        logger.info("=" * 60)
        logger.info("Browser Configuration")
        logger.info("=" * 60)
        logger.info(f"Environment: {env}")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Headless: {self.headless}")
        logger.info(f"CDP URL: {self.cdp_url or 'Not set'}")
        logger.info("")
        logger.info("Recommendation:")
        logger.info(f"  Mode: {recommendation['mode']}")
        logger.info(f"  Headless: {recommendation['headless']}")
        logger.info(f"  Note: {recommendation['note']}")
        if 'alternative' in recommendation:
            logger.info(f"  Alternative: {recommendation['alternative']}")
        logger.info("=" * 60)


# Global instance
_browser_config = None


def get_browser_config() -> BrowserConfig:
    """Get or create global browser config"""
    global _browser_config
    if _browser_config is None:
        _browser_config = BrowserConfig()
    return _browser_config


if __name__ == '__main__':
    # Print config when run directly
    logging.basicConfig(level=logging.INFO)
    config = get_browser_config()
    config.print_config_info()

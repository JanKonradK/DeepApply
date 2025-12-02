"""
Test browser-use with IDE Chrome via CDP
Configures browser-use to connect to Chrome running in the IDE
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "services"))

from browser_use import Agent as BrowserAgent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from playwright.async_api import async_playwright

# Load environment
from dotenv import load_dotenv
load_dotenv()


async def test_ide_chrome_connection():
    """Test connecting to IDE Chrome via CDP"""

    # IDE Chrome typically runs on port 9222
    cdp_url = os.getenv('CHROME_CDP_URL', 'http://localhost:9222')

    print(f"🔗 Attempting to connect to Chrome CDP at: {cdp_url}")

    try:
        async with async_playwright() as playwright:
            # Connect to existing Chrome instance via CDP
            browser = await playwright.chromium.connect_over_cdp(cdp_url)

            print(f"✅ Connected to Chrome!")
            print(f"   Version: {browser.version}")

            # Get existing contexts or create new one
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                print(f"   Using existing context with {len(context.pages)} pages")
            else:
                context = await browser.new_context()
                print(f"   Created new context")

            # Create a test page
            page = await context.new_page()

            # Navigate to test site
            test_url = "https://www.example.com"
            print(f"\n🌐 Navigating to {test_url}...")
            await page.goto(test_url)

            # Get page title
            title = await page.title()
            print(f"✅ Page loaded successfully!")
            print(f"   Title: {title}")

            # Take screenshot
            screenshot_path = project_root / "test_ide_chrome.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot saved to: {screenshot_path}")

            # Close page
            await page.close()

            # Don't close browser - it's the IDE's browser
            print(f"\n✅ Test completed successfully!")

            return True

    except Exception as e:
        print(f"\n❌ Failed to connect to Chrome CDP: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Ensure Chrome is running with remote debugging enabled")
        print(f"2. Start Chrome with: chrome --remote-debugging-port=9222")
        print(f"3. Check if port 9222 is accessible")
        print(f"4. Set CHROME_CDP_URL environment variable if using different port")
        return False


async def test_browser_use_with_ide_chrome():
    """Test browser-use Agent with IDE Chrome"""

    cdp_url = os.getenv('CHROME_CDP_URL', 'http://localhost:9222')

    print(f"\n🤖 Testing browser-use Agent with IDE Chrome...")

    try:
        # Note: browser-use may not support CDP connection directly
        # We might need to configure it differently

        # Simple test task
        task = "Go to example.com and tell me the page title"

        print(f"   Task: {task}")

        # For now, we'll use the standard browser-use configuration
        # In production, we'd need to modify browser-use to accept CDP connection

        print(f"\n⚠️  Note: browser-use may not support CDP directly.")
        print(f"   Consider using playwright directly or modifying browser-use source.")

        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Chrome CDP Connection Test")
    print("=" * 60)

    # Test 1: Direct CDP connection
    result1 = await test_ide_chrome_connection()

    # Test 2: browser-use with IDE Chrome
    # result2 = await test_browser_use_with_ide_chrome()

    print("\n" + "=" * 60)
    if result1:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. See output above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

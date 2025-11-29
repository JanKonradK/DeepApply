import os
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError

class TelegramNotifier:
    """
    Sends notifications to user via Telegram for manual intervention.
    """
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = Bot(token=self.bot_token) if self.bot_token else None

    async def send_message(self, message: str) -> bool:
        """Send a text message to the user."""
        if not self.bot:
            print("⚠️ Telegram bot not configured. Skipping notification.")
            return False

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print(f"📱 Telegram message sent: {message[:50]}...")
            return True
        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
            return False

    async def send_screenshot(self, screenshot_path: str, caption: str = "") -> bool:
        """Send a screenshot to the user."""
        if not self.bot:
            return False

        try:
            with open(screenshot_path, 'rb') as photo:
                await self.bot.send_photo(chat_id=self.chat_id, photo=photo, caption=caption)
            print(f"📸 Screenshot sent: {screenshot_path}")
            return True
        except Exception as e:
            print(f"❌ Screenshot send error: {e}")
            return False

    async def request_manual_intervention(
        self,
        issue_type: str,
        screenshot_path: Optional[str] = None,
        timeout_seconds: int = 300
    ) -> dict:
        """
        Notify user and wait for manual action.

        Returns:
            dict: {"action": "continue" | "skip" | "abort", "data": Optional[str]}
        """
        message = f"""
🚨 **Manual Intervention Needed**

Issue: {issue_type}

Please:
1. Review the screenshot below
2. Take necessary action in the browser
3. Reply with:
   - 'continue' to proceed
   - 'skip' to skip this application
   - 'abort' to stop all applications

You have {timeout_seconds // 60} minutes to respond.
        """

        await self.send_message(message)

        if screenshot_path:
            await self.send_screenshot(screenshot_path, caption=issue_type)

        # In a full implementation, this would listen for Telegram updates
        # For now, we return a timeout response
        print(f"⏳ Waiting {timeout_seconds}s for user response...")
        await asyncio.sleep(timeout_seconds)

        # TODO: Implement actual listener for user responses
        return {"action": "skip", "data": None}

    async def notify_completion(self, job_title: str, status: str):
        """Notify user of application completion."""
        emoji = "✅" if status == "success" else "⚠️"
        message = f"{emoji} Application to **{job_title}** - Status: {status}"
        await self.send_message(message)

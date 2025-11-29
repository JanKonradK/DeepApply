import asyncio
import os
from services.agent.src.utils.telegram_notifier import TelegramNotifier

async def test_telegram_fallback():
    print("🧪 Testing Telegram Fallback...")

    # Check credentials
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. Skipping test.")
        return

    notifier = TelegramNotifier()

    # 1. Send Alert
    print("1️⃣ Sending alert message...")
    success = await notifier.send_message("🚨 TEST ALERT: Agent is stuck! Please reply with 'fixed' to continue.")
    if success:
        print("✅ Alert sent successfully.")
    else:
        print("❌ Failed to send alert.")
        return

    # 2. Wait for Reply
    print("2️⃣ Waiting for your reply (timeout 60s)...")
    reply = await notifier.wait_for_reply(timeout=60)

    if reply:
        print(f"✅ Received reply: '{reply}'")
    else:
        print("❌ No reply received (timeout).")

if __name__ == "__main__":
    asyncio.run(test_telegram_fallback())

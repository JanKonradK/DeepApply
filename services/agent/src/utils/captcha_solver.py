import os
import asyncio
import requests
from typing import Dict, Any, Optional

class CaptchaSolver:
    """
    Handles CAPTCHA solving using the 2captcha API.
    Supports reCAPTCHA v2/v3, hCaptcha, and image-based challenges.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TWOCAPTCHA_API_KEY")
        self.base_url = "http://2captcha.com"

    async def solve_recaptcha(self, site_key: str, url: str, version: str = "v2") -> Dict[str, Any]:
        """
        Solves Google reCAPTCHA.
        """
        if not self.api_key:
            return {"error": "Missing 2captcha API key"}

        print(f"🧩 CaptchaSolver: Submitting reCAPTCHA {version}...")

        # 1. Submit request
        params = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": url,
            "json": 1
        }
        if version == "v3":
            params["version"] = "v3"
            params["action"] = "verify" # Default action

        try:
            resp = requests.post(f"{self.base_url}/in.php", params=params)
            request_id = resp.json().get("request")
        except Exception as e:
            return {"error": f"Submission failed: {str(e)}"}

        if not request_id:
             return {"error": f"Invalid response from 2captcha: {resp.text}"}

        # 2. Poll for result
        print(f"⏳ CaptchaSolver: Waiting for solution (ID: {request_id})...")
        for _ in range(20): # Wait up to 100s
            await asyncio.sleep(5)
            try:
                res_resp = requests.get(f"{self.base_url}/res.php", params={
                    "key": self.api_key,
                    "action": "get",
                    "id": request_id,
                    "json": 1
                })
                result = res_resp.json()

                if result.get("status") == 1:
                    print("✅ CaptchaSolver: Solved!")
                    return {"token": result.get("request")}

                if result.get("request") == "CAPCHA_NOT_READY":
                    continue
                else:
                    return {"error": f"Solving failed: {result.get('request')}"}
            except Exception as e:
                print(f"⚠️ CaptchaSolver: Polling error: {e}")

        return {"error": "Timeout waiting for CAPTCHA solution"}

    async def solve_image(self, image_b64: str) -> Dict[str, Any]:
        """
        Solves normal image CAPTCHA (text in image).
        """
        if not self.api_key:
            return {"error": "Missing 2captcha API key"}

        print("🧩 CaptchaSolver: Submitting image CAPTCHA...")

        params = {
            "key": self.api_key,
            "method": "base64",
            "body": image_b64,
            "json": 1
        }

        try:
            resp = requests.post(f"{self.base_url}/in.php", data=params)
            request_id = resp.json().get("request")
        except Exception as e:
            return {"error": f"Submission failed: {str(e)}"}

        if not request_id:
             return {"error": f"Invalid response: {resp.text}"}

        # Poll
        for _ in range(10):
            await asyncio.sleep(3)
            res_resp = requests.get(f"{self.base_url}/res.php", params={
                "key": self.api_key,
                "action": "get",
                "id": request_id,
                "json": 1
            })
            result = res_resp.json()
            if result.get("status") == 1:
                return {"text": result.get("request")}
            if result.get("request") != "CAPCHA_NOT_READY":
                return {"error": result.get("request")}

        return {"error": "Timeout"}

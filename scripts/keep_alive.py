"""
BankerEye - Streamlit & Render Keep-Alive Automation Script.

Launches a headless browser session to:
1. Ping and interact with the Streamlit Cloud frontend (https://bankereye.streamlit.app).
2. Detect if Streamlit has entered hibernation and automatically click "Yes, get this app back up!".
3. Ping the Flask backend on Render (https://bankereye-1.onrender.com/api/health) to prevent cold starts.
"""

import sys
import time
from playwright.sync_api import sync_playwright

FRONTEND_URL = "https://bankereye.streamlit.app"
BACKEND_HEALTH_URL = "https://bankereye-1.onrender.com/api/health"


def run_keep_alive():
    print(f"[Keep-Alive] Starting session check for: {FRONTEND_URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 1. Visit Streamlit frontend
        print(f"[Keep-Alive] Navigating to Streamlit frontend...")
        try:
            res = page.goto(FRONTEND_URL, wait_until="domcontentloaded", timeout=60000)
            status = res.status if res else "Unknown"
            print(f"[Keep-Alive] Frontend HTTP status: {status}")
            time.sleep(5)

            # Check for Streamlit sleep screen button
            wake_selectors = [
                "button:has-text('Yes, get this app back up!')",
                "button:has-text('get this app back up')",
                "button:has-text('Wake app back up')",
            ]

            wake_button = None
            for sel in wake_selectors:
                btn = page.locator(sel)
                if btn.count() > 0 and btn.first.is_visible():
                    wake_button = btn.first
                    break

            if wake_button:
                print("[Keep-Alive] [WARN] App is currently asleep! Clicking 'Yes, get this app back up!'...")
                wake_button.click()
                print("[Keep-Alive] Clicked wake-up button. Waiting 35 seconds for container reboot...")
                page.wait_for_timeout(35000)
                print("[Keep-Alive] [OK] Streamlit frontend woken up successfully!")
            else:
                print("[Keep-Alive] [OK] App is already active and awake! Interactive session established.")

            # Allow 5s for Streamlit websocket connection handshake
            time.sleep(5)

        except Exception as ex:
            print(f"[Keep-Alive] Frontend check encountered: {ex}")

        # 2. Ping Flask backend on Render
        print(f"[Keep-Alive] Pinging Flask backend on Render: {BACKEND_HEALTH_URL}...")
        try:
            res_backend = page.goto(BACKEND_HEALTH_URL, timeout=60000)
            status_b = res_backend.status if res_backend else "Unknown"
            print(f"[Keep-Alive] Backend health status: {status_b}")
        except Exception as ex:
            print(f"[Keep-Alive] Backend ping encountered: {ex}")

        browser.close()
        print("[Keep-Alive] [OK] Routine completed successfully.")


if __name__ == "__main__":
    run_keep_alive()

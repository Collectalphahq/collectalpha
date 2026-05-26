import os
import requests


DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()


def send_discord_alert(title: str, message: str):
    if not DISCORD_WEBHOOK:
        print("⚠️ Discord webhook missing. Alert skipped.")
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": 3066993,
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Discord alert sent.")
        return True
    except Exception as e:
        print(f"⚠️ Discord alert failed: {e}")
        return False
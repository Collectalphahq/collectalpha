import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_message(message: str):
    if not DISCORD_WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK is missing from .env")

    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

    if response.status_code not in [200, 204]:
        raise Exception(
            f"Discord alert failed: {response.status_code} - {response.text}"
        )

    return True
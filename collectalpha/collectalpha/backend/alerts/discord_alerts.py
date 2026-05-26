import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


def send_discord_embed(
    title,
    description,
    fields=None,
    image_url=None,
    color=15158332
):
    if not DISCORD_WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK missing from .env")

    embed = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {
            "text": "CollectAlpha Intelligence"
        }
    }

    if fields:
        embed["fields"] = fields

    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

    if response.status_code not in [200, 204]:
        raise Exception(
            f"Discord failed: {response.status_code} - {response.text}"
        )

    return True
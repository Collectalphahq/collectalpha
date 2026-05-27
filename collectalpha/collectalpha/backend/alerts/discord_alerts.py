import os
import requests


DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()


def send_discord_embed(title, description, fields=None, image_url=None):
    if not DISCORD_WEBHOOK:
        print("Discord webhook missing. Alert skipped.")
        return False

    embed = {
        "title": title,
        "description": description,
        "fields": fields or []
    }

    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=15)
        response.raise_for_status()
        print("Discord alert sent.")
        return True
    except Exception as e:
        print(f"Discord alert failed: {e}")
        return False
import random
import requests

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"


def fetch_card(card_id):
    url = f"{TCGDEX_BASE}/cards/{card_id}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    card = response.json()

    # Temporary mock pricing so scanner can test full flow before real price APIs.
    card["pricing"] = build_mock_pricing(card_id)

    return card


def build_mock_pricing(card_id):
    base_price = max(1, (sum(ord(char) for char in card_id) % 200) + 1)

    movement = random.uniform(0.85, 1.05)
    market_price = round(base_price * movement, 2)

    return {
        "tcgplayer": {
            "prices": {
                "normal": {
                    "market": market_price,
                    "mid": round(market_price * 1.05, 2),
                    "low": round(market_price * 0.9, 2),
                }
            }
        }
    }


def fetch_universe(limit=None):
    url = f"{TCGDEX_BASE}/cards"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    cards = response.json()

    filtered = []

    for card in cards:
        if limit is not None and len(filtered) >= limit:
            break

        if not card.get("id"):
            continue

        if not card.get("name"):
            continue

        filtered.append({
            "id": card["id"],
            "name": card["name"],
            "image": card.get("image")
        })

    return filtered

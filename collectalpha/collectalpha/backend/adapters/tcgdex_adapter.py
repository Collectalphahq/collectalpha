import requests

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"


def fetch_card(card_id):
    url = f"{TCGDEX_BASE}/cards/{card_id}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.json()


def fetch_universe(limit=250):
    url = f"{TCGDEX_BASE}/cards"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    cards = response.json()

    filtered = []

    for card in cards[:limit]:
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
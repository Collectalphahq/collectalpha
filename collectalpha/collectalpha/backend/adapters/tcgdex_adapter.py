import requests

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"


def fetch_card(card_id):
    url = f"{TCGDEX_BASE}/cards/{card_id}"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    return response.json()


def fetch_universe(limit=None):
    url = f"{TCGDEX_BASE}/cards"

    response = requests.get(url, timeout=40)
    response.raise_for_status()

    cards = response.json()
    filtered = []

    for card in cards:
        if limit is not None and len(filtered) >= limit:
            break

        card_id = card.get("id")
        card_name = card.get("name")

        if not card_id or not card_name:
            continue

        filtered.append({
            "id": card_id,
            "name": card_name,
            "image": card.get("image")
        })

    return filtered
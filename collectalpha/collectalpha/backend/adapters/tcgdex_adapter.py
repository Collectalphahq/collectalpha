import random
import requests

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"


def fetch_card(card_id):
    url = f"{TCGDEX_BASE}/cards/{card_id}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    card = response.json()

    # Temporary mock pricing so scanner can run before real price sources are connected.
    # This will be replaced later by real pricing adapters like eBay, TCGPlayer, PriceCharting, etc.
    card["pricing"] = build_mock_pricing(card_id)

    return card


def build_mock_pricing(card_id):
    # Creates a fake but stable-ish test price based on the card id.
    # This lets the scanner save history, compare old/current prices, and test alerts.
    base_price = max(1, (sum(ord(char) for char in card_id) % 200) + 1)

    # Small random movement each scan.
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
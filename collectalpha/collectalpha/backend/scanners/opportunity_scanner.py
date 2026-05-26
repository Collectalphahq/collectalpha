import json
from pathlib import Path
from datetime import datetime

from backend.alerts.discord_alerts import send_discord_embed
from backend.adapters.tcgdex_adapter import fetch_card

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

UNIVERSE_FILE = DATA_DIR / "pokemon_universe.json"
PRICE_HISTORY_FILE = DATA_DIR / "market_price_history.json"


def load_json(path, default):
    if not path.exists():
        return default

    with open(path, "r") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=2)


def extract_raw_price(card):
    pricing = card.get("pricing", {})

    tcgplayer = pricing.get("tcgplayer", {})
    if tcgplayer:
        prices = tcgplayer.get("prices", {})

        for variant in prices.values():
            if isinstance(variant, dict):
                for key in ["market", "mid", "low"]:
                    if variant.get(key):
                        return float(variant[key]), "TCGplayer"

    cardmarket = pricing.get("cardmarket", {})
    if cardmarket:
        prices = cardmarket.get("prices", {})

        for key in ["averageSellPrice", "trendPrice", "avg7", "avg30"]:
            if prices.get(key):
                return float(prices[key]), "Cardmarket"

    return None, None


def calculate_drop(old_price, current_price):
    if not old_price or old_price <= 0:
        return 0

    return round(((old_price - current_price) / old_price) * 100, 2)


def calculate_score(drop_percent):
    score = 40

    if drop_percent >= 10:
        score += 30

    if drop_percent >= 15:
        score += 15

    return min(score, 100)


def scan_market(limit=100):
    universe = load_json(UNIVERSE_FILE, [])[:limit]
    history = load_json(PRICE_HISTORY_FILE, {})

    for item in universe:
        card_id = item["id"]

        try:
            card = fetch_card(card_id)
        except Exception as e:
            print(f"Failed {card_id}: {e}")
            continue

        current_price, source = extract_raw_price(card)

        if current_price is None:
            print(f"No price for {item['name']}")
            continue

        card_key = f"{item['name']} {card_id} RAW"

        old_price = history.get(card_key, {}).get("last_price")

        history[card_key] = {
            "last_price": current_price,
            "source": source,
            "last_checked": datetime.utcnow().isoformat()
        }

        if old_price is None:
            print(f"Saved first price: {card_key}")
            continue

        drop_percent = calculate_drop(old_price, current_price)
        score = calculate_score(drop_percent)

        if drop_percent >= 10 and score >= 70:
            image_url = None

            if card.get("image"):
                image_url = card["image"] + "/high.webp"

            send_discord_embed(
                title="🚨 CollectAlpha RAW Opportunity",
                description="Real market movement detected.",
                fields=[
                    {"name": "Card", "value": item["name"], "inline": True},
                    {"name": "Card ID", "value": card_id, "inline": True},
                    {"name": "Source", "value": source, "inline": True},
                    {"name": "Previous", "value": f"${old_price}", "inline": True},
                    {"name": "Current", "value": f"${current_price}", "inline": True},
                    {"name": "Drop", "value": f"{drop_percent}%", "inline": True},
                    {"name": "Score", "value": f"{score}/100", "inline": True},
                ],
                image_url=image_url,
            )

            print(f"ALERT: {item['name']}")

    save_json(PRICE_HISTORY_FILE, history)


if __name__ == "__main__":
    scan_market()
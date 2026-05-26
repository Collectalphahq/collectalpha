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

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Failed to load JSON file {path}: {e}")
        return default


def save_json(path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
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
    opportunities = []

    print(f"Loaded {len(universe)} cards from universe.")

    for item in universe:
        card_id = item.get("id")
        card_name = item.get("name", "Unknown Card")

        if not card_id:
            print(f"Skipping item with missing card id: {item}")
            continue

        try:
            card = fetch_card(card_id)
        except Exception as e:
            print(f"Failed {card_id}: {e}")
            continue

        current_price, source = extract_raw_price(card)

        if current_price is None:
            print(f"No price for {card_name}")
            continue

        card_key = f"{card_name} {card_id} RAW"
        old_price = history.get(card_key, {}).get("last_price")

        history[card_key] = {
            "last_price": current_price,
            "source": source,
            "last_checked": datetime.utcnow().isoformat()
        }

        if old_price is None:
            print(f"Saved first price: {card_key} | ${current_price}")
            continue

        drop_percent = calculate_drop(old_price, current_price)
        score = calculate_score(drop_percent)

        print(
            f"Checked {card_name}: old=${old_price}, "
            f"current=${current_price}, drop={drop_percent}%, score={score}"
        )

        if drop_percent >= 10 and score >= 70:
            image_url = None

            if card.get("image"):
                image_url = card["image"] + "/high.webp"

            opportunity = {
                "card": card_name,
                "card_id": card_id,
                "source": source,
                "previous_price": old_price,
                "current_price": current_price,
                "drop_percent": drop_percent,
                "score": score,
                "image_url": image_url,
            }

            opportunities.append(opportunity)

            send_discord_embed(
                title="🚨 CollectAlpha RAW Opportunity",
                description="Real market movement detected.",
                fields=[
                    {"name": "Card", "value": card_name, "inline": True},
                    {"name": "Card ID", "value": card_id, "inline": True},
                    {"name": "Source", "value": source, "inline": True},
                    {"name": "Previous", "value": f"${old_price}", "inline": True},
                    {"name": "Current", "value": f"${current_price}", "inline": True},
                    {"name": "Drop", "value": f"{drop_percent}%", "inline": True},
                    {"name": "Score", "value": f"{score}/100", "inline": True},
                ],
                image_url=image_url,
            )

            print(f"ALERT: {card_name}")

    save_json(PRICE_HISTORY_FILE, history)

    print(f"Scan finished. Opportunities found: {len(opportunities)}")

    return opportunities


if __name__ == "__main__":
    scan_market()
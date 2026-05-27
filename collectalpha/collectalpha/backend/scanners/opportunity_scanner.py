import json
from pathlib import Path
from datetime import datetime

from backend.alerts.discord_alerts import send_discord_embed
from backend.adapters.tcgdex_adapter import fetch_card, fetch_universe
from backend.adapters.ebay_adapter import search_ebay_items

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
        print(f"Failed to load JSON from {path}: {e}")
        return default


def save_json(path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def build_full_universe():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Building full Pokémon universe from TCGdex...")

    universe = fetch_universe(limit=None)

    save_json(UNIVERSE_FILE, universe)

    print(f"Saved full Pokémon universe with {len(universe)} cards.")

    return universe


def load_or_build_universe(rebuild_universe=False):
    if rebuild_universe:
        return build_full_universe()

    universe = load_json(UNIVERSE_FILE, [])

    if not universe:
        print("Universe file missing or empty. Building full universe...")
        return build_full_universe()

    print(f"Loaded saved universe with {len(universe)} cards.")
    return universe


def extract_raw_price(card):
    pricing = card.get("pricing", {})

    tcgplayer = pricing.get("tcgplayer", {})
    if isinstance(tcgplayer, dict) and tcgplayer:
        for variant_key in [
            "normal",
            "holofoil",
            "reverse-holofoil",
            "1st-edition",
            "unlimited",
        ]:
            variant = tcgplayer.get(variant_key)

            if isinstance(variant, dict):
                for price_key in ["market", "mid", "low"]:
                    value = variant.get(price_key)

                    if value:
                        return float(value), f"TCGplayer {variant_key}"

        prices = tcgplayer.get("prices", {})
        if isinstance(prices, dict):
            for variant_name, variant in prices.items():
                if isinstance(variant, dict):
                    for price_key in ["market", "mid", "low"]:
                        value = variant.get(price_key)

                        if value:
                            return float(value), f"TCGplayer {variant_name}"

    cardmarket = pricing.get("cardmarket", {})
    if isinstance(cardmarket, dict) and cardmarket:
        prices = cardmarket.get("prices", {})

        if isinstance(prices, dict):
            for price_key in [
                "averageSellPrice",
                "trendPrice",
                "avg7",
                "avg30",
                "lowPrice",
            ]:
                value = prices.get(price_key)

                if value:
                    return float(value), "Cardmarket"

    return None, None

def get_ebay_market_price(card_name):
    query = f"{card_name} Pokemon card"

    try:
        items = search_ebay_items(query, limit=10)
    except Exception as e:
        print(f"eBay search failed for {card_name}: {e}")
        return None, None, []

    if not items:
        return None, None, []

    prices = [item["price"] for item in items if item.get("price")]

    if not prices:
        return None, None, items

    avg_price = round(sum(prices) / len(prices), 2)

    return avg_price, "eBay Active Listings", items

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


def scan_market(limit=None, rebuild_universe=False):
    universe = load_or_build_universe(rebuild_universe=rebuild_universe)

    if limit is not None:
        universe = universe[:limit]

    history = load_json(PRICE_HISTORY_FILE, {})
    opportunities = []

    total_cards = len(universe)
    priced_cards = 0
    skipped_no_price = 0
    failed_cards = 0

    print(f"Starting market scan. Cards to scan: {total_cards}")

    for index, item in enumerate(universe, start=1):
        card_id = item.get("id")
        card_name = item.get("name", "Unknown Card")

        if not card_id:
            print(f"Skipping item with missing card id: {item}")
            continue

        try:
            card = fetch_card(card_id)
        except Exception as e:
            failed_cards += 1
            print(f"Failed to fetch {card_name} ({card_id}): {e}")
            continue

        current_price, source = extract_raw_price(card)
        ebay_items = []

        if current_price is None:
            current_price, source, ebay_items = get_ebay_market_price(card_name)

        if current_price is None:
            skipped_no_price += 1
            print(f"No real price for {card_name} ({card_id})")
            continue

        priced_cards += 1

        card_key = f"{card_name} {card_id} RAW"
        old_price = history.get(card_key, {}).get("last_price")

        history[card_key] = {
            "last_price": current_price,
            "source": source,
            "last_checked": datetime.utcnow().isoformat()
        }

        if old_price is None:
            print(f"[{index}/{total_cards}] Saved first real price: {card_key} | ${current_price}")
            continue

        drop_percent = calculate_drop(old_price, current_price)
        score = calculate_score(drop_percent)

        print(
            f"[{index}/{total_cards}] Checked {card_name}: "
            f"old=${old_price}, current=${current_price}, "
            f"drop={drop_percent}%, score={score}"
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
                "ebay_items": ebay_items[:3],
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

    print(
        f"Scan finished. "
        f"Total={total_cards}, "
        f"Priced={priced_cards}, "
        f"NoPrice={skipped_no_price}, "
        f"Failed={failed_cards}, "
        f"Opportunities={len(opportunities)}"
    )

    return {
        "opportunities": opportunities,
        "total_cards": total_cards,
        "priced_cards": priced_cards,
        "skipped_no_price": skipped_no_price,
        "failed_cards": failed_cards,
    }


if __name__ == "__main__":
    scan_market(limit=None, rebuild_universe=False)
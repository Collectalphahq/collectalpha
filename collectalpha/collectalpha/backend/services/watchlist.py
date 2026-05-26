import json
from pathlib import Path


WATCHLIST_PATH = Path("backend/data/watchlist.json")


def load_watchlist():
    if not WATCHLIST_PATH.exists():
        print("⚠️ No watchlist found.")
        return []

    with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    print(f"✅ Loaded {len(cards)} cards from watchlist.")
    return cards
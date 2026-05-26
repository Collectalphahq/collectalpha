from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.adapters.tcgdex_adapter import fetch_universe


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UNIVERSE_FILE = DATA_DIR / "pokemon_universe.json"


def build_universe(limit=250):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Building Pokémon universe with limit={limit}...")

    cards = fetch_universe(limit=limit)

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as file:
        json.dump(cards, file, indent=2)

    print(f"Saved {len(cards)} cards to {UNIVERSE_FILE}")


if __name__ == "__main__":
    build_universe(limit=250)
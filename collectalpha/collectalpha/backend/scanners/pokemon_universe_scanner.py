import requests
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

UNIVERSE_FILE = DATA_DIR / "pokemon_universe.json"

TCGDEX_API = "https://api.tcgdex.net/v2/en/cards"


def fetch_pokemon_universe(limit=250):
    response = requests.get(TCGDEX_API, timeout=20)
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


def save_universe(cards):
    with open(UNIVERSE_FILE, "w") as file:
        json.dump(cards, file, indent=2)


def main():
    cards = fetch_pokemon_universe()
    save_universe(cards)

    print(f"Saved {len(cards)} Pokémon cards.")


if __name__ == "__main__":
    main()
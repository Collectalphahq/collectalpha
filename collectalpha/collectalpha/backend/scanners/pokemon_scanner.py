import requests
from backend.alerts.discord_alerts import send_discord_message

TCGDEX_API = "https://api.tcgdex.net/v2/en/cards"


def fetch_pokemon_cards(limit=20):
    response = requests.get(TCGDEX_API, timeout=15)
    response.raise_for_status()

    cards = response.json()

    return cards[:limit]


def simulate_market_data(card):
    import random

    current_price = round(random.uniform(20, 500), 2)
    old_price = round(current_price * random.uniform(1.05, 1.25), 2)

    drop_percent = ((old_price - current_price) / old_price) * 100

    return {
        "name": card["name"],
        "current_price": current_price,
        "old_price": old_price,
        "drop_percent": round(drop_percent, 2)
    }


def calculate_rebound_score(drop_percent):
    score = 50

    if drop_percent >= 10:
        score += 20

    if drop_percent >= 15:
        score += 10

    return min(score, 100)


def scan_market():
    cards = fetch_pokemon_cards()

    for card in cards:
        data = simulate_market_data(card)

        if data["drop_percent"] >= 10:
            rebound_score = calculate_rebound_score(data["drop_percent"])

            if rebound_score >= 70:
                message = f"""
🚨 REBOUND ALERT

Card: {data['name']}
Old Price: ${data['old_price']}
Current Price: ${data['current_price']}
Drop: {data['drop_percent']}%
Rebound Score: {rebound_score}/100
"""

                send_discord_message(message)
                print(f"Alert sent for {data['name']}")


if __name__ == "__main__":
    scan_market()
def fetch_universe(limit=None):
    url = f"{TCGDEX_BASE}/cards"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    cards = response.json()

    filtered = []

    for card in cards:
        if limit is not None and len(filtered) >= limit:
            break

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
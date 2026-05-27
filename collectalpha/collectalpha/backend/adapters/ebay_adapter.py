import base64
import os
import requests


ENABLE_EBAY = os.getenv("ENABLE_EBAY", "false").strip().lower() == "true"

EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID", "").strip()
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET", "").strip()
EBAY_MARKETPLACE_ID = os.getenv("EBAY_MARKETPLACE_ID", "EBAY_US").strip()

EBAY_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def ebay_is_configured():
    return all([
        ENABLE_EBAY,
        EBAY_CLIENT_ID,
        EBAY_CLIENT_SECRET,
        EBAY_MARKETPLACE_ID,
    ])


def get_ebay_access_token():
    if not ebay_is_configured():
        print("eBay adapter disabled or missing credentials.")
        return None

    credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    response = requests.post(
        EBAY_OAUTH_URL,
        headers=headers,
        data=data,
        timeout=20,
    )

    response.raise_for_status()

    token_data = response.json()
    return token_data.get("access_token")


def search_ebay_items(query, limit=10):
    token = get_ebay_access_token()

    if not token:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": EBAY_MARKETPLACE_ID,
    }

    params = {
        "q": query,
        "limit": str(limit),
        "filter": "buyingOptions:{FIXED_PRICE}",
    }

    response = requests.get(
        EBAY_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()
    items = data.get("itemSummaries", [])

    results = []

    for item in items:
        price_data = item.get("price", {})
        price_value = price_data.get("value")

        if not price_value:
            continue

        try:
            price = float(price_value)
        except ValueError:
            continue

        results.append({
            "title": item.get("title"),
            "price": price,
            "currency": price_data.get("currency"),
            "url": item.get("itemWebUrl"),
            "condition": item.get("condition"),
            "source": "eBay",
        })

    return results
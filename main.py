import requests
from bs4 import BeautifulSoup
import json

url = "https://www.facebook.com/marketplace/GEO_ID/search/?query=QUERY"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://duckduckgo.com/",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "TE": "trailers",
}

session = requests.Session()
response = session.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

script_tags = soup.find_all("script", {"type": "application/json", "data-sjs": True})

all_listings = []


def extract_from_edges_nodes(data):
    if isinstance(data, dict):
        if "feed_units" in data:
            for edge in data["feed_units"].get("edges", []):
                all_listings.append(edge["node"])

        # Recursively check other dictionary items
        for value in data.values():
            extract_from_edges_nodes(value)

    elif isinstance(data, list):
        for item in data:
            extract_from_edges_nodes(item)


for tag in script_tags:
    try:
        json_data = json.loads(tag.string)
        extract_from_edges_nodes(json_data)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        continue

all_listings = [listing for listing in all_listings if listing]


formatted_listings = []

for listing_data in all_listings:
    listing = listing_data.get("listing", {})
    listing_name = listing.get("marketplace_listing_title")
    price = listing.get("listing_price", {}).get("formatted_amount")
    listing_picture = (
        listing.get("primary_listing_photo", {}).get("image", {}).get("uri")
    )
    id = listing.get("id")
    location = listing.get("location", {}).get("reverse_geocode", {}).get("city")

    formatted_listings.append(
        {
            "name": listing_name,
            "price": price,
            "listing_picture": listing_picture,
            "id": id,
            "location": location,
        }
    )

print(len(formatted_listings))

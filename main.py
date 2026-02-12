import requests
from bs4 import BeautifulSoup
import json
import os
import re

URL = "https://www.major-expert.ru/buy/"
BASE = "https://www.major-expert.ru"
MAX_PRICE = 5000000

TOKEN = "8447981017:AAH8HboVB0LTZwdHCO7G4tGYrPJQq9oaKSg"
CHAT_ID = "1436689911"


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )


def parse_price(text):
    numbers = re.sub(r"[^\d]", "", text)
    if numbers:
        return int(numbers)
    return None


def get_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ads = []

    cards = soup.find_all("a", href=True)

    for card in cards:
        href = card["href"]

        if "/cars/" in href:
            link = BASE + href
            text = card.get_text(" ", strip=True)

            price = parse_price(text)
            if price and price <= MAX_PRICE:
                ads.append({
                    "link": link,
                    "price": price,
                    "title": text[:150]
                })

    return ads


def load_old():
    if not os.path.exists("ads.json"):
        return []
    with open("ads.json", "r") as f:
        return json.load(f)


def save_ads(ads):
    with open("ads.json", "w") as f:
        json.dump(ads, f)


def main():
    old_ads = load_old()
    old_links = [ad["link"] for ad in old_ads]

    new_ads = get_ads()

    fresh = [ad for ad in new_ads if ad["link"] not in old_links]

    for ad in fresh:
        message = f"""
<b>{ad['title']}</b>

💰 {format(ad['price'], ",").replace(",", " ")} ₽

🔗 {ad['link']}
"""
        send_telegram(message)

    save_ads(new_ads)


if __name__ == "__main__":
    main()

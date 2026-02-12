import requests
from bs4 import BeautifulSoup
import json
import os
import re

URL = "https://www.major-expert.ru/buy/"
BASE = "https://www.major-expert.ru"

MIN_PRICE = 100000
MAX_PRICE = 3000000

TOKEN = "8447981017:AAH8HboVB0LTZwdHCO7G4tGYrPJQq9oaKSg"
CHAT_ID = "1436689911"


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True
        }
    )


def extract_price(text):
    match = re.search(r"([\d\s]+)\s*руб", text)
    if match:
        return int(match.group(1).replace(" ", ""))
    return None


def get_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ads = []

    for card in soup.find_all("a", href=True):
        href = card["href"]

        if "/cars/" in href:
            full_text = card.get_text(" ", strip=True)

            price = extract_price(full_text)
            if price and MIN_PRICE <= price <= MAX_PRICE:
                link = BASE + href

                ads.append({
                    "link": link,
                    "price": price,
                    "text": full_text
                })

    return ads


def load_old():
    try:
        with open("ads.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_ads(ads):
    with open("ads.json", "w") as f:
        json.dump(ads, f)


def main():
    old_ads = load_old()
    old_links = [ad["link"] for ad in old_ads]

    new_ads = get_ads()

    fresh = [ad for ad in new_ads if ad["link"] not in old_links]

    for ad in fresh:
        message = f"{format(ad['price'], ',').replace(',', ' ')} руб. | {ad['text']}\n{ad['link']}"
        send_telegram(message)

    save_ads(new_ads)


if __name__ == "__main__":
    main()

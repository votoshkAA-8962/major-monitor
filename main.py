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

DB_FILE = "sent_ads.json"


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


def extract_id(link):
    match = re.search(r"/cars/(\d+)", link)
    if match:
        return match.group(1)
    return None


def load_sent():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []


def save_sent(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)


def get_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ads = []

    for card in soup.find_all("a", href=True):
        href = card["href"]

        if "/cars/" in href:
            link = BASE + href
            full_text = card.get_text(" ", strip=True)

            price = extract_price(full_text)
            if price and MIN_PRICE <= price <= MAX_PRICE:

                ad_id = extract_id(link)

                ads.append({
                    "id": ad_id,
                    "link": link,
                    "price": price,
                    "text": full_text
                })

    return ads


def main():
    sent_ads = load_sent()
    new_ads = get_ads()

    updated_sent = sent_ads.copy()

    for ad in new_ads:
        if ad["id"] not in sent_ads:
            message = f"{format(ad['price'], ',').replace(',', ' ')} руб. | {ad['text']}\n{ad['link']}"
            send_telegram(message)
            updated_sent.append(ad["id"])

    save_sent(updated_sent)


if __name__ == "__main__":
    main()

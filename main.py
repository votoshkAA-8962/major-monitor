import requests
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://new.major-expert.ru/api/items-by-url"

PRICE_MIN = 100000
PRICE_MAX = 5000000

DB_FILE = "sent_ads.json"


def load_sent():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(json.load(f))


def save_sent(sent_ids):
    with open(DB_FILE, "w") as f:
        json.dump(list(sent_ids), f)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })


def get_cars():
    params = {"url": "/cars/moscow/"}
    r = requests.get(API_URL, params=params, timeout=15)
    data = r.json()
    return data["data"]["items"]


def format_message(car):
    price = car.get("price", 0)
    name = car.get("fullName", "Без названия")
    car_id = car.get("id")

    link = f"https://new.major-expert.ru/cars/{car_id}/"
    text = f"{price:,} руб. | {name} {link}"
    return text.replace(",", " ")


def main():
    sent_ids = load_sent()
    print("Проверка объявлений...")

    cars = get_cars()

    for car in cars:
        car_id = car.get("id")
        price = car.get("price", 0)

        if price < PRICE_MIN or price > PRICE_MAX:
            continue

        if car_id in sent_ids:
            continue

        message = format_message(car)
        send_telegram(message)

        print("Новое объявление:", message)
        sent_ids.add(car_id)

    save_sent(sent_ids)


if __name__ == "__main__":
    main()

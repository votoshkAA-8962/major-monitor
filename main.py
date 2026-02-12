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
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_sent(sent_ids):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_ids), f, ensure_ascii=False, indent=2)


def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Нет BOT_TOKEN или CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })

    if response.status_code != 200:
        print("Ошибка Telegram:", response.text)


def get_cars():
    params = {"url": "/cars/moscow/"}
    r = requests.get(API_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data["data"]["items"]


def format_message(car):
    price = car.get("price", 0)
    name = car.get("fullName", "Без названия")
    car_id = car.get("id")

    link = f"https://new.major-expert.ru/cars/{car_id}/"
    text = f"{price:,} руб.\n{name}\n{link}"
    return text.replace(",", " ")


def main():
    sent_ids = load_sent()
    print("🔍 Проверка объявлений...")

    cars = get_cars()
    new_count = 0

    for car in cars:
        car_id = car.get("id")
        price = car.get("price", 0)

        if not car_id:
            continue

        if price < PRICE_MIN or price > PRICE_MAX:
            continue

        if car_id in sent_ids:
            continue

        message = format_message(car)
        send_telegram(message)

        sent_ids.add(car_id)
        new_count += 1
        print("Новое объявление:", car_id)

    save_sent(sent_ids)
    print(f"Готово. Найдено новых: {new_count}")


if __name__ == "__main__":
    main()

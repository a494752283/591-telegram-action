
import os, requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

def fetch_new_listings():
    url = "https://land.591.com.tw/list?region=6&type=1&kind=11"
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for card in soup.select(".property-list-item"):
        title = card.select_one(".infoContent h3").get_text(strip=True)
        time_text = card.select_one(".infoContent .postDate").get_text(strip=True)
        if "今天" in time_text or "小時前" in time_text:
            price = card.select_one(".price").get_text(strip=True)
            link = "https://land.591.com.tw" + card.select_one("a")["href"]
            items.append(f"{title} — {price} — {time_text}\n{link}")
    return items

def send_to_telegram(msgs):
    if not msgs:
        bot.send_message(chat_id=CHAT_ID, text="🔔 今日無新土地物件上架。")
    else:
        text = "📅 今日新土地物件：\n\n" + "\n\n".join(msgs)
        bot.send_message(chat_id=CHAT_ID, text=text)

if __name__ == "__main__":
    listings = fetch_new_listings()
    send_to_telegram(listings)

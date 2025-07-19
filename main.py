import os
import requests
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# 查詢縣市代碼（台北=1、新北=3、桃園=6、基隆=4、宜蘭=21）
REGIONS = {
    "台北市": 1,
    "新北市": 3,
    "桃園市": 6,
    "基隆市": 4,
    "宜蘭縣": 21,
}

def fetch_api(region_id):
    url = "https://bff.land.591.com.tw/v1/house/list"
    params = {
        "region": region_id,
        "type": 1,
        "kind": 11,
        "is_format_data": 1,
        "firstRow": 0,
        "totalRows": 0
    }
    headers = {
        "origin": "https://land.591.com.tw",
        "referer": "https://land.591.com.tw/",
        "user-agent": "Mozilla/5.0",
        "accept": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", {}).get("data", [])
    except Exception as e:
        print(f"[{region_id}] 無法取得資料: {e}")
        return []

def filter_today(items):
    new_items = []
    for i in items:
        time_note = i.get("ltime", "")
        if time_note and "天" not in time_note:  # 只要「今天」、「小時前」、「分鐘前」
            title = i.get("address", "無地址")
            price = i.get("price", "無價格")
            unit = i.get("unit", "")
            link = f"https://land.591.com.tw/home/{i.get('post_id')}"
            new_items.append(f"{title} — {price}{unit} — {time_note}\n{link}")
    return new_items

def send_to_telegram(all_items):
    if not all_items:
        bot.send_message(chat_id=CHAT_ID, text="🔔 今日五縣市土地出租無新物件上架。")
    else:
        text = "📅 今日五縣市土地出租新物件：\n\n" + "\n\n".join(all_items)
        bot.send_message(chat_id=CHAT_ID, text=text)

if __name__ == "__main__":
    all_data = {k: fetch_api(v) for k, v in REGIONS.items()}
    all_items = []
    for city, items in all_data.items():
        filtered = filter_today(items)
        all_items.extend([f"[{city}] {x}" for x in filtered])
    send_to_telegram(all_items)

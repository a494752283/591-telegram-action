
import os, requests, asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

REGIONS = {
    "台北市": 1,
    "新北市": 3,
    "桃園市": 6,
    "基隆市": 2,
    "宜蘭縣": 21
}

HEADERS = {
    "User-Agent": "591land/1.0",
    "Device": "pc",
    "Origin": "https://land.591.com.tw",
    "Referer": "https://land.591.com.tw",
}

def fetch_api(region_id):
    url = "https://bff.land.591.com.tw/v1/house/list"
    params = {
        "region": region_id,
        "type": 1,   # 出租
        "kind": 11,  # 土地
        "is_format_data": 1,
        "firstRow": 0,
        "totalRows": 0
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        return []
    data = resp.json().get("data", {}).get("items", [])
    new_items = []
    for d in data:
        post_time = d.get("ltime")
        title = d.get("address", "")
        price = d.get("price", "")
        unit = d.get("priceUnit", "")
        link = f"https://rent.591.com.tw/rent-detail-{d.get('houseid')}.html"
        if post_time and "分鐘" in post_time or "小時" in post_time or "今天" in post_time:
            new_items.append(f"{title} — {price}{unit} — {post_time}\n{link}")
    return new_items

async def send_to_telegram(region_map):
    if not any(region_map.values()):
        await bot.send_message(chat_id=CHAT_ID, text="📅 今日無新土地物件上架。")
    else:
        messages = ["📅 今日新土地物件彙整："]
        for region, items in region_map.items():
            if items:
                messages.append(f"🏙️ {region}（{len(items)} 筆）:")
                messages.extend(items)
                messages.append("")  # 空行分隔
        await bot.send_message(chat_id=CHAT_ID, text="\n".join(messages[:20]))

if __name__ == "__main__":
    all_data = {k: fetch_api(v) for k, v in REGIONS.items()}
    asyncio.run(send_to_telegram(all_data))

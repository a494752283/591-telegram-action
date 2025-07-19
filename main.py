
import os, requests, asyncio
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

REGIONS = {
    "台北市": 1,
    "新北市": 3,
    "基隆市": 2,
    "桃園市": 6,
    "宜蘭縣": 21
}

def fetch_listings(region_id):
    url = f"https://land.591.com.tw/list?region={region_id}&type=1&kind=11"
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    listings = []
    for card in soup.select(".property-list-item"):
        title = card.select_one(".infoContent h3").get_text(strip=True)
        time_text = card.select_one(".infoContent .postDate").get_text(strip=True)
        # 包含：今天、小時前、1~6天前
        if "今天" in time_text or "小時" in time_text or "天前" in time_text:
            try:
                if "天前" in time_text:
                    days = int(time_text.replace("天前", ""))
                    if days > 6:
                        continue
                price = card.select_one(".price").get_text(strip=True)
                link = "https://land.591.com.tw" + card.select_one("a")["href"]
                listings.append(f"{title} — {price} — {time_text}\n{link}")
            except Exception:
                continue
    return listings

async def send_to_telegram(region_data):
    if not region_data:
        await bot.send_message(chat_id=CHAT_ID, text="🔔 近 7 天無新土地物件上架。")
    else:
        parts = []
        for region_name, items in region_data.items():
            if items:
                parts.append(f"📍 {region_name}：\n" + "\n\n".join(items))
        text = "📅 近 7 天新土地物件彙整：\n\n" + "\n\n".join(parts)
        await bot.send_message(chat_id=CHAT_ID, text=text[:4096])

if __name__ == "__main__":
    result = {}
    for name, region_id in REGIONS.items():
        result[name] = fetch_listings(region_id)
    asyncio.run(send_to_telegram(result))

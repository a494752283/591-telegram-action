
import os, requests, asyncio
from bs4 import BeautifulSoup
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

def fetch_listings_by_region(region_id):
    url = f"https://land.591.com.tw/list?region={region_id}&type=1&kind=11"
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    listings = []
    for card in soup.select(".property-list-item"):
        time_text = card.select_one(".infoContent .postDate").get_text(strip=True)
        if any(day in time_text for day in ["今天", "小時前", "1天前", "2天前", "3天前", "4天前", "5天前", "6天前"]):
            title = card.select_one(".infoContent h3").get_text(strip=True)
            price = card.select_one(".price").get_text(strip=True)
            link = "https://land.591.com.tw" + card.select_one("a")["href"]
            listings.append(f"{title} — {price} — {time_text}\n{link}")
    return listings

async def send_to_telegram(region_map):
    if not any(region_map.values()):
        await bot.send_message(chat_id=CHAT_ID, text="📅 近 7 天無新土地物件上架。")
    else:
        messages = ["📅 近 7 天土地物件彙整："]
        for region, items in region_map.items():
            if items:
                messages.append(f"🏙️ {region}（{len(items)} 筆）:")
                messages.extend(items)
                messages.append("")  # 空行分隔
        await bot.send_message(chat_id=CHAT_ID, text="\n".join(messages[:20]))  # 限制 4096 字元

if __name__ == "__main__":
    data = {name: fetch_listings_by_region(region_id) for name, region_id in REGIONS.items()}
    asyncio.run(send_to_telegram(data))

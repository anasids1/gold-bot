
import requests
from bs4 import BeautifulSoup

def get_gold_prices(parse_only=False):
    url = "https://www.jjsjo.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")[1:]
    prices = {}
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            karat = cols[0].text.strip()
            sell_price = float(cols[1].text.strip().split()[0])
            buy_price = float(cols[2].text.strip().split()[0])
            if "24" in karat:
                prices["24k_sell"] = sell_price
                prices["24k_buy"] = buy_price
            elif "21" in karat:
                prices["21k_sell"] = sell_price
                prices["21k_buy"] = buy_price
            elif "18" in karat:
                prices["18k_sell"] = sell_price
                prices["18k_buy"] = buy_price
            elif "14" in karat:
                prices["14k_sell"] = sell_price
                prices["14k_buy"] = buy_price
    if parse_only:
        return prices
    return (
        "أسعار الذهب اليوم في الأردن (ذهب صافي بدون مصنعية):\n\n"
        f"🔸 24 K: بيع {prices.get('24k_sell', '؟')} دينار | شراء {prices.get('24k_buy', '؟')} دينار\n"
        f"🔸 21 K: بيع {prices.get('21k_sell', '؟')} دينار | شراء {prices.get('21k_buy', '؟')} دينار\n"
        f"🔸 18 K: بيع {prices.get('18k_sell', '؟')} دينار | شراء {prices.get('18k_buy', '؟')} دينار\n"
        f"🔸 14 K: بيع {prices.get('14k_sell', '؟')} دينار | شراء {prices.get('14k_buy', '؟')} دينار\n"
    )

def calculate_gold_buy_price(karat: str, weight: float):
    prices = get_gold_prices(parse_only=True)
    key = f"{karat.lower()}_buy"
    if key in prices:
        total = round(prices[key] * weight, 2)
        return f"💰 السعر التقريبي لبيع {weight}غ من ذهب {karat.upper()} هو: {total} دينار"
    return "⚠️ لم يتم العثور على سعر لهذا العيار."

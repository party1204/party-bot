import requests
import time
import schedule
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from random import choice

# ה-TOKEN של הבוט שלך מ-BotFather בטלגרם
TOKEN = '8168907258:AAGBOlvovBQSF-5bUSj3B04yfnMFlogoCIE'  # ה-TOKEN שלך

# ה-chat_id של הקבוצה שלך בטלגרם
CHAT_ID = '-4710675866'  # ה-chat_id של הקבוצה שלך (החלף בזה שלך)

# מזהה השותף שלך ב-AliExpress (החלף עם מזהה השותף שלך)
AFFILIATE_ID = 'my_party'  # מזהה השותף שלך באלי אקספרס

# יצירת אובייקט של בוט עם ה-TOKEN שלך
bot = Bot(token=TOKEN)

# פונקציה לחיפוש מוצרים באלי אקספרס לפי קטגוריות
def fetch_products():
    categories = ["wedding", "party", "birthday", "event", "event-accessories"]
    all_products = []

    for category in categories:
        url = f"https://api.aliexpress.com/product/search?keywords={category}&aff_id={AFFILIATE_ID}"
        response = requests.get(url)
        if response.status_code == 200:
            products = response.json()
            if 'items' in products:
                all_products.extend(products['items'])
    
    return all_products

# פונקציה לשליחת קישורים לקבוצה
def send_links():
    products = fetch_products()
    # בוחרים 3 מוצרים אקראיים
    selected_products = [choice(products) for _ in range(3)]

    for product in selected_products:
        product_name = product.get('title', 'No title available')
        product_link = product.get('link', 'No link available')
        bot.send_message(chat_id=CHAT_ID, text=f"Check this product: {product_name}\n{product_link}")

# תזמון שליחת מוצרים כל 8 שעות (שלוש פעמים ביום)
schedule.every(8).hours.do(send_links)

# הרצת תזמון כל הזמן
while True:
    schedule.run_pending()
    time.sleep(60)

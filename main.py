import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from telegram import Bot
from urllib.parse import quote
import os
import random
import time

# הגדרות
BOT_TOKEN = "8168907258:AAGBOlvovBQSF-5bUSj3B04yfnMFlogoCIE"  # טוקן הבוט שלך
CHAT_ID = "4710675866"  # מזהה הקבוצה שלך בטלגרם
ADMITAD_BASE = "https://rzekl.com/g/1e8d11449475164bd74316525dc3e8/"  # הקישור שלך ב-Admitad
AFFILIATE_ID = "my_party"  # ה-Affiliate ID שלך ב-AliExpress
SENT_FILE = "sent_products.txt"  # קובץ המוצרים שנשלחו

bot = Bot(token=BOT_TOKEN)
scheduler = BackgroundScheduler(timezone=timezone("Asia/Jerusalem"))

# טעינת מוצרים שנשלחו
def load_sent_products():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

# שמירת מוצר שנשלח
def save_sent_product(product_id):
    with open(SENT_FILE, "a", encoding="utf-8") as f:
        f.write(product_id + "\n")

# יצירת קישור אפילייאט מותאם אישית
def generate_affiliate_link(url):
    encoded = quote(url, safe='')  # קידוד ה-URL
    return f"{ADMITAD_BASE}?ulp={encoded}"

# ניסוח הודעה שיווקית מותאמת עם טיפ לאפליקציה
def generate_rich_text(title, price, link):
    emojis = ["🔥", "✅", "🛒", "💡", "✨", "📦", "❤️", "⚡", "🚀", "⭐"]
    intro = random.choice([
        "תעצור הכל – זה משהו שאתה פשוט חייב להכיר",
        "מצאתי לך את המוצר שכולם מדברים עליו",
        "כזה דבר לא רואים כל יום – ויש סיבה לזה",
        "הדבר הקטן הזה? הולך לשדרג לך את היום",
        "אם אתה אוהב דברים חכמים ושימושיים – זה בדיוק בשבילך"
    ])
    detail = random.choice([
        "מלא בסטייל, שימושי בטירוף, והכי חשוב – במחיר שבא לפנק",
        "נראה טוב, עובד מעולה, וכל מי שניסה פשוט עף",
        "רמה גבוהה, מחיר נמוך – מה צריך יותר?",
        "זה פשוט עובד. בלי שטויות. בלי חרטות.",
        "כל מי שקנה – חזר לעוד אחד"
    ])
    cta = random.choice([
        "הקישור פה למטה – תלחץ ותגלה",
        "זה הולך להיגמר – תפס לפני כולם",
        "קח הצצה – תבין לבד למה כולם עפים על זה",
        "אני כבר בפנים. אתה?",
        "הזדמנות כזו לא חוזרת פעמיים"
    ])
    tips = [
        "🧠 טיפ: הכי נוח להזמין דרך האפליקציה – תפתח את הקישור דרך AliExpress",
        "📱 שים לב: עדיף לפתוח את הקישור מהאפליקציה כדי לראות מחיר טוב יותר",
        "⚡ פתחת את הקישור בדפדפן? נסה דרך אפליקציית AliExpress – הרבה יותר נוח",
        "🚀 רוצים משלוח מהיר? האפליקציה לפעמים מציגה אפשרויות טובות יותר",
        "🛍️ לפעמים המחיר באפליקציה נמוך יותר – שווה לנסות משם"
    ]
    tip = random.choice(tips)

    lines = [
        f"{random.choice(emojis)} {intro}",
        f"{random.choice(emojis)} {title}",
        f"{random.choice(emojis)} {detail}"
    ]
    if price:
        lines.append(f"{random.choice(emojis)} מחיר: {price}")
    lines.append(f"{random.choice(emojis)} <a href='{link}'>לצפייה במוצר</a>")
    lines.append(f"{random.choice(emojis)} {cta}")
    lines.append(tip)
    return "\n".join(lines)

# שליפת מחיר
def get_price(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.select_one("meta[property='product:price:amount']")
        return f"{tag['content']} ₪" if tag else None
    except:
        return None

# שליפת תמונה
def get_image(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.find("meta", property="og:image")
        return tag["content"] if tag else None
    except:
        return None

# שליפת מוצרים טרנדיים לפי קטגוריות
def get_trending_products(limit=3):
    sent = load_sent_products()
    categories = [
        "אביזרים לחתונות",
        "אביזרים לאירועים",
        "מיתוג",
        "אירועים",
        "אביזרים לימי הולדת",
        "שילוט"
    ]
    
    products = []
    
    for category in categories:
        url = f"https://www.aliexpress.com/wholesale?SearchText={category.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("a[href*='/item/']")
        
        for link in links:
            href = link.get("href")
            if not href.startswith("http"):
                href = "https:" + href
            title = link.get("title") or link.text.strip()
            if not title:
                continue
            product_id = (title.lower()).replace(" ", "_")
            if product_id in sent:
                continue
            price = get_price(href)
            image = get_image(href)
            if not image:  # אם אין תמונה לא נשלח את המוצר
                continue
            affiliate_link = generate_affiliate_link(href)
            rich_text = generate_rich_text(title, price, affiliate_link)

            # שליחה לטלגרם
            bot.send_message(chat_id=CHAT_ID, text=rich_text, parse_mode="HTML")
            save_sent_product(product_id)

            products.append({
                "title": title,
                "link": affiliate_link,
                "price": price,
                "image": image
            })
            if len(products) >= limit:
                break

    return products

# הגדרת משימה מתוזמנת לשליפת מוצרים כל 8 שעות
def start_scheduler():
    scheduler.add_job(get_trending_products, 'interval', hours=8)
    scheduler.start()

if __name__ == "__main__":
    # הרצת הפונקציה לשלוח 3 מוצרים מיד עם הפעלת הקוד
    get_trending_products()
    
    # מנגנון הממתין עד שהמשימה המתוזמנת רצה
    start_scheduler()

    while True:
        time.sleep(60)  # השהייה של 60 שניות

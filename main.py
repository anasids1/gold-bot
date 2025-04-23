
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from gold_scraper import get_gold_prices, calculate_gold_buy_price

TOKEN = "7386691728:AAHmv5Fmv_au5W0EzTcTlvwgNlNRpcTPlKU"

CHOOSING_KARAT, TYPING_WEIGHT, MODE = range(3)
user_data = {}
ADMIN_ID = 6980170289

# SQLite setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
conn.commit()

def is_admin(user_id):
    return user_id == ADMIN_ID

def save_user(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                   (user_id, username))
    conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, f"@{user.username}" if user.username else "")

    keyboard = [
        [InlineKeyboardButton("📈 أسعار الذهب", callback_data="prices")],
        [InlineKeyboardButton("🥇 سعر ليرة رشادي", callback_data="rashadi")],
        [InlineKeyboardButton("🥇 سعر ليرة إنجليزي", callback_data="english")],
        [InlineKeyboardButton("💰 بيع الذهب", callback_data="sell_gold")],
        [InlineKeyboardButton("🛒 شراء الذهب", url="https://t.me/anasids")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "أهلاً بك في بوت أسعار الذهب في الأردن 🇯🇴\n\n"
        "اختر من القائمة التالية:\n\n"
        "Developed by: @anasids"
    )

    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "prices":
        prices = get_gold_prices(parse_only=True)
        text = (
            "أسعار الذهب اليوم في الأردن (ذهب صافي بدون مصنعية):\n\n"
            f"🔸 24 K: بيع {prices.get('24k_sell', '؟')} دينار | شراء {prices.get('24k_buy', '؟')} دينار\n"
            f"🔸 21 K: بيع {prices.get('21k_sell', '؟')} دينار | شراء {prices.get('21k_buy', '؟')} دينار\n"
            f"🔸 18 K: بيع {prices.get('18k_sell', '؟')} دينار | شراء {prices.get('18k_buy', '؟')} دينار\n"
            f"🔸 14 K: بيع {prices.get('14k_sell', '؟')} دينار | شراء {prices.get('14k_buy', '؟')} دينار\n"
        )
        await query.edit_message_text(text=text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]))

    elif data == "rashadi":
        prices = get_gold_prices(parse_only=True)
        rashadi = round(prices.get("21k_sell", 0) * 7 + 4, 1)
        await query.edit_message_text(
            text=f"🥇 سعر ليرة رشادي (وزن 7غ): {rashadi} دينار\n📩 للاستفسار: @anasids",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]])
        )

    elif data == "english":
        prices = get_gold_prices(parse_only=True)
        english = round(prices.get("21k_sell", 0) * 8 + 4, 1)
        await query.edit_message_text(
            text=f"🥇 سعر ليرة إنجليزي (وزن 8غ): {english} دينار\n📩 للاستفسار: @anasids",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]])
        )

    elif data == "sell_gold":
        keyboard = [
            [InlineKeyboardButton("24K", callback_data="karat_24k")],
            [InlineKeyboardButton("21K", callback_data="karat_21k")],
            [InlineKeyboardButton("18K", callback_data="karat_18k")],
            [InlineKeyboardButton("14K", callback_data="karat_14k")]
        ]
        await query.edit_message_text("اختر عيار الذهب الذي ترغب ببيعه:", reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_KARAT

    elif data.startswith("karat_"):
        karat = data.split("_")[1]
        user_data["karat"] = karat
        await query.edit_message_text("الرجاء إدخال وزن الذهب بالغرام:")
        return TYPING_WEIGHT

    elif data == "main_menu":
        await start(update, context)

async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weight_str = update.message.text.strip()
    karat = user_data.get("karat")

    try:
        weight = float(weight_str)
        result = calculate_gold_buy_price(karat, weight)
        keyboard = [
            [InlineKeyboardButton("🔁 إدخال وزن آخر", callback_data=f"karat_{karat}")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await update.message.reply_text(result + "\n📩 للاستفسار: @anasids", reply_markup=InlineKeyboardMarkup(keyboard))
    except ValueError:
        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح للوزن.")
        return TYPING_WEIGHT

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        cursor.execute("SELECT username FROM users")
        users = cursor.fetchall()
        usernames = [u[0] for u in users if u[0]]
        count = len(usernames)
        users_text = "\n".join(usernames) if usernames else "لا يوجد أسماء مستخدمين."
        await update.message.reply_text(f"📋 قائمة المستخدمين ({count}):\n\n{users_text}")
    else:
        await update.message.reply_text("🚫 هذا الأمر مخصص للمطوّر فقط.")

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if is_admin(user_id) and text.startswith("الكل "):
        message = text.replace("الكل ", "", 1).strip()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        for uid in user_ids:
            try:
                await context.bot.send_message(chat_id=uid, text=message)
            except:
                continue
    else:
        await start(update, context)

async def check_price_changes(context: ContextTypes.DEFAULT_TYPE):
    prices = get_gold_prices(parse_only=True)
    last_prices = context.application_data.get("last_prices", {})

    if prices != last_prices:
        context.application_data["last_prices"] = prices
        text = (
            "📢 تحديث تلقائي لأسعار الذهب في الأردن:\n\n"
            f"🔸 24 K: بيع {prices.get('24k_sell', '؟')} | شراء {prices.get('24k_buy', '؟')}\n"
            f"🔸 21 K: بيع {prices.get('21k_sell', '؟')} | شراء {prices.get('21k_buy', '؟')}\n"
            f"🔸 18 K: بيع {prices.get('18k_sell', '؟')} | شراء {prices.get('18k_buy', '؟')}\n"
            f"🔸 14 K: بيع {prices.get('14k_sell', '؟')} | شراء {prices.get('14k_buy', '؟')}\n"
        )
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        for uid in user_ids:
            try:
                await context.bot.send_message(chat_id=uid, text=text)
            except:
                continue

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_buttons)],
        states={
            CHOOSING_KARAT: [CallbackQueryHandler(handle_buttons)],
            TYPING_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weight)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", show_users))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message))
    app.job_queue.run_repeating(check_price_changes, interval=300, first=10)
    app.run_polling()

if __name__ == '__main__':
    main()


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)
import logging
from gold_scraper import get_gold_prices

# إعداد اللوق
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7386691728:AAHmv5Fmv_au5W0EzTcTlvwgNlNRpcTPlKU"

# دالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 أسعار الذهب", callback_data='prices')],
        [InlineKeyboardButton("🧮 حاسبة الذهب", callback_data='calculator')],
        [InlineKeyboardButton("📉 بيع الذهب", callback_data='sell')],
        [InlineKeyboardButton("📈 شراء الذهب", callback_data='buy')],
        [InlineKeyboardButton("🥇 سعر الليرة الرشادي", callback_data='rashadi')],
        [InlineKeyboardButton("👑 سعر الليرة الإنجليزي", callback_data='english')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحبًا بك! اختر من القائمة:", reply_markup=reply_markup)

# دالة استجابة للأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'prices':
        prices = get_gold_prices()
        message = "\n".join([f"{k}: {v}" for k, v in prices.items()])
        await query.edit_message_text(text=f"💰 أسعار الذهب:\n\n{message}")
    elif data == 'rashadi':
        prices = get_gold_prices()
        await query.edit_message_text(f"🥇 سعر الليرة الرشادي: {prices.get('ليرة رشادي', 'غير متوفر')}")
    elif data == 'english':
        prices = get_gold_prices()
        await query.edit_message_text(f"👑 سعر الليرة الإنجليزي: {prices.get('ليرة إنجليزي', 'غير متوفر')}")
    else:
        await query.edit_message_text("📌 هذه الميزة قيد التطوير.")

# دالة التحقق من تغير الأسعار
async def check_price_changes(context: ContextTypes.DEFAULT_TYPE):
    prices = get_gold_prices()
    message = "\n".join([f"{k}: {v}" for k, v in prices.items()])
    for user_id in context.application.bot_data.get("subscribers", []):
        try:
            await context.bot.send_message(chat_id=user_id, text=f"💰 تم تحديث أسعار الذهب:\n\n{message}")
        except Exception as e:
            logging.warning(f"فشل الإرسال للمستخدم {user_id}: {e}")

# نقطة البداية
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # إعداد JobQueue للمقارنة التلقائية
    job_queue = app.job_queue
    job_queue.run_repeating(check_price_changes, interval=300, first=10)

    app.run_polling()

if __name__ == '__main__':
    main()

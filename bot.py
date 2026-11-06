import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ضع هنا الـ Token الخاص ببوت تيليجرام
TOKEN = "9033036280:AAF6wkoKFuRuJj8oVKQLZHVGziKlJqQLdj0"

# ضع هنا رابط الـ npoint الذي حصلت عليه
NPOINT_URL = "https://jsonblob.com/01a1b2f8-b68c-7e39-ae8d-69a6ae6865b4"


class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running successfully!")


def run_web_server():
    port = int(os.environ.get("PORT", 7860))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"Web server running on port {port}...")
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("حالة الشحن", callback_data="charging_menu")],
        [InlineKeyboardButton("نسبة الشحن", callback_data="level_menu")],
        [InlineKeyboardButton("حالة الشاشة", callback_data="screen_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك في لوحة تحكم ومراقبة هاتفك المنزلي\nاختر ما تحب مراقبته:",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "charging_menu":
        keyboard = [
            [InlineKeyboardButton("الحالة الآنية (طلب تحديث)", callback_data="get_live_data")],
            [InlineKeyboardButton("عرض آخر تحديث محفوظ", callback_data="get_live_data")],
            [InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="back_home")],
        ]
        await query.edit_message_text(text="قائمة حالة الشحن:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "level_menu":
        keyboard = [
            [InlineKeyboardButton("النسبة الآنية (طلب تحديث)", callback_data="get_live_data")],
            [InlineKeyboardButton("عرض آخر نسبة محفوظة", callback_data="get_live_data")],
            [InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="back_home")],
        ]
        await query.edit_message_text(text="قائمة نسبة البطارية:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "screen_menu":
        keyboard = [
            [InlineKeyboardButton("حالة الشاشة الآنية", callback_data="get_live_data")],
            [InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="back_home")],
        ]
        await query.edit_message_text(text="قائمة حالة الشاشة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "back_home":
        keyboard = [
            [InlineKeyboardButton("حالة الشحن", callback_data="charging_menu")],
            [InlineKeyboardButton("نسبة الشحن", callback_data="level_menu")],
            [InlineKeyboardButton("حالة الشاشة", callback_data="screen_menu")],
        ]
        await query.edit_message_text(text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "get_live_data":
        try:
            response = requests.get(NPOINT_URL)
            data = response.json()
            
            level = data.get("level", "--")
            charging = data.get("charging", "--")
            screen = data.get("screen", "--")
            time_val = data.get("time", "--")

            msg = (
                f"📊 *تقرير حالة الهاتف المنزلي*\n\n"
                f"🔋 *النسبة:* {level}%\n"
                f"⚡ *الحالة:* {charging}\n"
                f"📱 *الشاشة:* {screen}\n\n"
                f"⏰ *وقت القياس:* {time_val}"
            )
            await query.message.reply_text(text=msg, parse_mode="Markdown")
        except Exception as e:
            await query.message.reply_text(text="⚠️ حدث خطأ أثناء جلب البيانات من السحابة.")


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("البوت يعمل الآن بنجاح على السحابة...")
    app.run_polling()

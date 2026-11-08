import csv
import io
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

TOKEN = "9033036280:AAF6wkoKFuRuJj8oVKQLZHVGziKlJqQLdj0"

# ضع هنا رابط النشر (CSV) الذي حصلت عليه من Google Sheets
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1gEk5SDKzkD1X1NjD0YTbfQyM5yX8TyVndS0P99WVkJ0/edit?usp=sharing
"


class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running successfully!")


def run_web_server():
    port = int(os.environ.get("PORT", 7860))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔋 حالة الشحن والشاشة", callback_data="get_live_data")],
        [InlineKeyboardButton("🔄 تحديث القائمة", callback_data="back_home")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك في لوحة تحكم ومراقبة هاتفك المنزلي 🏠\nاضغط على الزر أدناه لجلب الحالة الآنية:",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_home":
        keyboard = [
            [InlineKeyboardButton("🔋 حالة الشحن والشاشة", callback_data="get_live_data")],
        ]
        await query.edit_message_text(text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == "get_live_data":
        try:
            # جلب بيانات الشيت بصيغة CSV
            res = requests.get(SHEET_CSV_URL)
            res.encoding = 'utf-8'
            
            # قراءة الأسطر من ملف CSV
            csv_file = io.StringIO(res.text)
            reader = list(csv.reader(csv_file))

            # أخذ آخر صف مكتوب في الجدول (أحدث سجل)
            last_row = reader[-1]

            # مطابقة الأعمدة بناءً على صورتك:
            # العمود A: device_id (index 0)
            # العمود B: battery_level_percent (index 1)
            # العمود C: charging (index 2)
            # العمود D: page_visibility (index 3)
            # العمود F: client_time_iso (index 5)
            
            device_id = last_row[0] if len(last_row) > 0 else "غير معروف"
            level = last_row[1] if len(last_row) > 1 else "--"
            charging_val = last_row[2] if len(last_row) > 2 else "False"
            screen_state = last_row[3] if len(last_row) > 3 else "--"
            time_val = last_row[5] if len(last_row) > 5 else "--"

            # تحويل قيمة charging من True/False إلى لغة واضحة
            charging_text = "يشحن 🔌" if charging_val.upper() == "TRUE" else "على البطارية 🔋"
            
            # تحويل حالة الشاشة
            screen_text = "نشطة / مفتوحة ☀️" if screen_state == "visible" else "مقفلة / في الخلفية 🌙"

            msg = (
                f"📊 *تقرير حالة الهاتف المنزلي*\n\n"
                f"📱 *الجهاز:* {device_id}\n"
                f"🔋 *النسبة:* {level}%\n"
                f"⚡ *الحالة:* {charging_text}\n"
                f"👁️ *الشاشة:* {screen_text}\n\n"
                f"⏰ *الوقـت:* {time_val}"
            )

            keyboard = [[InlineKeyboardButton("🔄 تحديث البيانات", callback_data="get_live_data")]]
            await query.message.reply_text(text=msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as e:
            await query.message.reply_text(text="⚠️ حدث خطأ أثناء جلب البيانات من Google Sheets. تأكد من صحة الرابط.")


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ضع هنا الـ Token الخاص بك
TOKEN = "9033036280:AAF6wkoKFuRuJj8oVKQLZHVGziKlJqQLdj0"


# --- جزء سيرفر الويب البسيط لإبقاء الحاوية نشطة على Hugging Face ---
class DummyHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(
        b"Bot is active and running on Hugging Face Spaces successfully!"
    )


def run_web_server():
  port = int(os.environ.get("PORT", 7860))
  server = HTTPServer(("0.0.0.0", port), DummyHandler)
  print(f"Web server running on port {port}...")
  server.serve_forever()


# --- كود بوت تيليجرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [InlineKeyboardButton("🔋 حالة الشحن", callback_data="charging_menu")],
      [InlineKeyboardButton("⚡ نسبة الشحن", callback_data="level_menu")],
      [InlineKeyboardButton("📱 حالة الشاشة", callback_data="screen_menu")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text(
      "أهلاً بك في لوحة تحكم ومراقبة هاتفك المنزلي 🏠\nاختر ما تحب مراقبته:",
      reply_markup=reply_markup,
  )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  if query.data == "charging_menu":
    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 الحالة الآنية (طلب تحديث)",
                callback_data="get_live_charging",
            )
        ],
        [
            InlineKeyboardButton(
                "📂 عرض آخر تحديث محفوظ", callback_data="get_last_charging"
            )
        ],
        [InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_home")],
    ]
    await query.edit_message_text(
        text="قائمة حالة الشحن:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

  elif query.data == "level_menu":
    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 النسبة الآنية (طلب تحديث)", callback_data="get_live_level"
            )
        ],
        [
            InlineKeyboardButton(
                "📂 عرض آخر نسبة محفوظة", callback_data="get_last_level"
            )
        ],
        [InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_home")],
    ]
    await query.edit_message_text(
        text="قائمة نسبة البطارية:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

  elif query.data == "back_home":
    keyboard = [
        [InlineKeyboardButton("🔋 حالة الشحن", callback_data="charging_menu")],
        [InlineKeyboardButton("⚡ نسبة الشحن", callback_data="level_menu")],
        [InlineKeyboardButton("📱 حالة الشاشة", callback_data="screen_menu")],
    ]
    await query.edit_message_text(
        text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

  elif query.data in ["get_live_charging", "get_last_charging", "get_live_level"]:
    await query.message.reply_text(
        "⏳ جاري جلب البيانات من الهاتف المنزلي...\n(القيمة الحالية: 85% - يشحن"
        " 🔌)\n⏰ الوقت: 07:15 م"
    )


if __name__ == "__main__":
  # تشغيل سيرفر الويب في خلفية منفصلة (Thread)
  server_thread = threading.Thread(target=run_web_server, daemon=True)
  server_thread.start()

  # تشغيل بوت تيليجرام
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))

  print("البوت يعمل الآن بنجاح على السحابة...")
  app.run_polling()

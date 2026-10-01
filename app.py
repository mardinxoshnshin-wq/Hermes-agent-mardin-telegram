import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# ۱. راه‌اندازی وب‌سرور برای بیدار نگه داشتن برنامه در Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Agent is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ۲. تنظیم کلید Gemini
gemini_api_key = os.environ.get("GEMINI_API_KEY")
ai_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

# ۳. دستورات ربات تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ایجنت هرمس هستم. چطور می‌توانم کمکتان کنم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if not ai_client:
        await update.message.reply_text("خطا: کلید API جمینای تنظیم نشده است.")
        return
        
    try:
        # استفاده از مدل جدید Gemini 3.8 Flash
        response = ai_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=user_text,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"خطایی رخ داد: {str(e)}")

if __name__ == '__main__':
    # اجرای وب‌سرور در پس‌زمینه
    Thread(target=run_flask).start()
    
    # اجرای ربات تلگرام
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

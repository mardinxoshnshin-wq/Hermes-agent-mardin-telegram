import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from hermes_agent import HermesAgent

# ۱. وب‌سرور برای زنده نگه داشتن برنامه در Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Agent (Powered by Gemini 3.6 Flash) is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ۲. اتصال Hermes Agent به مدل Gemini 3.6 Flash
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

agent = HermesAgent(
    provider="google",               # استفاده از سرویس نیتیو گوگل
    model="gemini-3.6-flash",        # مدل Gemini 3.6 Flash
    api_key=api_key
)

# ۳. پاسخ‌دهی تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من Hermes Agent هستم که از مدل Gemini 3.6 Flash نیرو می‌گیرم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # پردازش پیام توسط ایجنت هرمس (همراه با حافظه و ابزارها)
        response = await agent.run(user_text)
        await update.message.reply_text(str(response))
    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش ایجنت: {str(e)}")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

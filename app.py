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
    return "Hermes Agent is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ۲. مقداردهی اولیه ایجنت هرمس
# می‌توان کلید Together AI، Groq یا OpenAI را برای ارائه مدل پایه هرمس داد
api_key = os.environ.get("HERMES_API_KEY") or os.environ.get("GEMINI_API_KEY")
agent = HermesAgent(api_key=api_key)

# ۳. هندل کردن پیام‌های تلگرام توسط Hermes Agent
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ایجنت هرمس (Nous Research) هستم. چطور می‌توانم کمکتان کنم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # ارسال ورودی کاربر به ایجنت اصلی هرمس
        response = await agent.run(user_text)
        await update.message.reply_text(str(response))
    except Exception as e:
        await update.message.reply_text(f"خطا در اجرای ایجنت: {str(e)}")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

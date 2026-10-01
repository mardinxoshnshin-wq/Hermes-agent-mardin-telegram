import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# ۱. وب‌سرور برای زنده نگه داشتن پروژه در Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Agent (Powered by Gemini 3.6 Flash) is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ۲. اتصال به API جمینای
gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
ai_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

SYSTEM_INSTRUCTION = """
شما ایجنت هرمس (Hermes Agent) هستید؛ یک دستیار هوشمند، حرفه‌ای و قدرتمند در تلگرام.
به تمامی سوالات کاربر با دقت، هوشمندی و لحنی محترمانه پاسخ دهید.
"""

# ۳. پاسخ‌دهی تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ایجنت هرمس هستم. چطور می‌توانم کمکتان کنم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if not ai_client:
        await update.message.reply_text("خطا: کلید API جمینای تنظیم نشده است.")
        return
        
    try:
        # فراخوانی مدل 3.6 Flash
        response = ai_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        if response and response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("پاسخی دریافت نشد.")
            
    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش: {str(e)}")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if bot_token:
        application = ApplicationBuilder().token(bot_token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.run_polling()

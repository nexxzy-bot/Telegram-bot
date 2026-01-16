import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из Railway
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Привет! Я AI-бот. Задай мне вопрос!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Помощь: просто напиши вопрос, я отвечу с помощью DeepSeek AI.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        await update.message.chat.send_action(action="typing")
        
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": 1500
        }
        
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            # Обрезаем для Telegram
            if len(answer) > 4000:
                answer = answer[:4000] + "\n\n...(сообщение обрезано)"
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f"Ошибка {response.status_code}. Попробуй позже.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Ошибка. Попробуй еще раз.")

def main():
    print("=== Запуск Telegram бота ===")
    print(f"Telegram токен: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"DeepSeek ключ: {'✅' if DEEPSEEK_API_KEY else '❌'}")
    
    if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
        print("❌ Ошибка: Токены не найдены!")
        print("Добавьте в Railway Variables:")
        print("1. TELEGRAM_TOKEN=ваш_токен")
        print("2. DEEPSEEK_API_KEY=ваш_ключ")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен! Ищи в Telegram.")
    app.run_polling()

if __name__ == '__main__':
    main()

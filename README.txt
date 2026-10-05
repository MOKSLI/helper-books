HELPER BOOKS — Telegram AI bot

Files:
- bot.py — the bot
- requirements.txt — libraries

Render settings:
Build Command:
    pip install -r requirements.txt

Start Command:
    uvicorn bot:app --host 0.0.0.0 --port $PORT

Environment variables:
BOT_TOKEN = Telegram bot token from BotFather
GEMINI_API_KEY = Google Gemini API key
WEBHOOK_SECRET = any long random string (optional)

Important:
Do not put tokens directly into bot.py or upload them to GitHub.

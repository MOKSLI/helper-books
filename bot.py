import os
import logging
from fastapi import FastAPI, Request
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "helper-books-secret")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()
telegram_app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я умный помощник. Напиши мне вопрос — постараюсь помочь."
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        return

    try:
        response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=f"""
Ты дружелюбный русскоязычный помощник.
Всегда отвечай пользователю на русском языке, если он не попросил другой язык.
Отвечай понятно и по делу.

Сообщение пользователя:
{text}
"""
    )

    answer = response.text or "Не смог сформировать ответ."

    for i in range(0, len(answer), 4000):
        await update.message.reply_text(answer[i:i+4000])

except Exception as e:
    logging.exception("AI request failed")

    await update.message.reply_text(
        "Похоже, ИИ сейчас временно занят 😅 "
        "Попробуй отправить сообщение ещё раз через несколько секунд."
        )

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()
    base_url = os.environ.get("RENDER_EXTERNAL_URL")
    if base_url:
        await telegram_app.bot.set_webhook(
            url=f"{base_url}/telegram/{WEBHOOK_SECRET}"
        )

@app.on_event("shutdown")
async def shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()

@app.get("/")
async def health():
    return {"ok": True, "service": "helper-books-bot"}

@app.post("/telegram/{secret}")
async def telegram_webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        return {"ok": False}
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

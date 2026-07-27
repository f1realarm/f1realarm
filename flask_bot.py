from flask import Flask, request
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from openai import OpenAI
import anthropic
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "ТВОЙ_ТОКЕН")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "ТВОЙ_КЛЮЧ")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "ТВОЙ_КЛЮЧ")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
user_model = {}

flask_app = Flask(__name__)
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! /gpt или /claude чтобы выбрать модель")

async def set_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_model[update.effective_user.id] = "gpt"
    await update.message.reply_text("Выбран ChatGPT ✅")

async def set_claude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_model[update.effective_user.id] = "claude"
    await update.message.reply_text("Выбран Claude ✅")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    model = user_model.get(user_id, "gpt")
    text = update.message.text

    if model == "gpt":
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": text}]
        )
        reply = response.choices[0].message.content
    else:
        response = claude_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": text}]
        )
        reply = response.content[0].text

    await update.message.reply_text(reply)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("gpt", set_gpt))
telegram_app.add_handler(CommandHandler("claude", set_claude))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@flask_app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok"

@flask_app.route("/")
def index():
    return "Bot is running"

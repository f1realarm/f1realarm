import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from openai import OpenAI
import anthropic

TELEGRAM_TOKEN = "ТВОЙ_ТОКЕН_TELEGRAM"
OPENAI_API_KEY = "ТВОЙ_КЛЮЧ_OPENAI"
ANTHROPIC_API_KEY = "ТВОЙ_КЛЮЧ_ANTHROPIC"

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Храним выбор модели для каждого пользователя
user_model = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выбери модель командой:\n"
        "/gpt — ChatGPT\n"
        "/claude — Claude\n"
        "Потом просто пиши сообщения."
    )

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

    await update.message.chat.send_action("typing")

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

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gpt", set_gpt))
    app.add_handler(CommandHandler("claude", set_claude))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if name == "__main__":
    main()
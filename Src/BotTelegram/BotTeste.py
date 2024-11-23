import requests
import time
import sqlite3
import pandas as pd
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')
bot = Bot(token=TOKEN)

async def send_telegram_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text, message_thread_id=TOPIC_ID)
async def main():
    try:
        while True:
            mensagem = "Mensagem de teste"
            await send_telegram_message(mensagem)
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("Parando a execução...")

asyncio.run(main())

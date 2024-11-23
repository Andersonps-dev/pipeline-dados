import telebot
import time
from datetime import datetime
import os
import requests
import scrapy
import time
import pandas as pd
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
import schedule
import time
import schedule

class NotifyOfferBot:
    def __init__(self):
        load_dotenv()

    def __estancia_bot(self):
        self.TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
        self.TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')
        self.bot = Bot(token=self.TOKEN)

    async def __enviar_telegram_message(self, text):
        await self.bot.send_message(chat_id=self.CHAT_ID, text=text, message_thread_id=self.TOPIC_ID)

    async def agendador(self):
        await self.__enviar_telegram_message("Mensagem aqui")
        await asyncio.sleep(10)

    def envio_posts(self):
        asyncio.run(self.agendador())
import pandas as pd
import sqlite3
from datetime import datetime
import requests
import time
import pandas as pd
import asyncio
from telegram import Bot
import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
import sqlite3
import asyncio
from telegram import Bot
from tabulate import tabulate

class NotifyOfferBot:
    def __init__(self):
        load_dotenv()
        self.__estancia_bot()

    def __estancia_bot(self):
        self.TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
        self.TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')

        self.bot = Bot(token=self.TOKEN)

    async def __enviar_telegram_message(self, text):
        await self.bot.send_message(chat_id=self.CHAT_ID, text=text, message_thread_id=self.TOPIC_ID)

    def criar_conexao_sqlite3(self, db_name):
        conn = sqlite3.connect(db_name)
        return conn
    
    def filtro_envios_principais(self):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        cursor.execute("SELECT *, (preco_anterior-preco_atual) as desconto_reais FROM  dados_casa_moveis_decoracao WHERE porcentagem_desconto >= 40 or desconto_reais >= 600 ORDER BY porcentagem_desconto DESC LIMIT 100")
        resultado = cursor.fetchall()

        cursor.close()
        return resultado

    def filtro_envios_reservas(self):
        pass

    def verificar_itens_novos(self):
        pass

    async def envios_telegram(self):
        for i in self.filtro_envios_principais():
            titulo = i[2]
            link = i[3]
            vendido_por = i[4]
            preco_antigo = i[7]
            preco_novo = i[8]
            porcentagem_desconto = i[9]
            detalhe_envio = i[10]
            detalhe_envio_2 = i[11]
            await self.__enviar_telegram_message(
                f"<h3><b>{titulo}</b></h3>\n\n"
                f"🔥 Por apenas <b>R$ {preco_novo}</b> 🔥\n\n"
                f"Preço antigo: <s>R$ {preco_antigo}</s> - Produto com <b>{porcentagem_desconto}%</b> de desconto.\n\n"
                f"{detalhe_envio}\n\n"
                f"{detalhe_envio_2}\n\n"
                f"Vendido pela loja oficial: <b>{vendido_por}</b>\n\n"
                f"🛒 Compre seu produto agora mesmo acessando o <a href='{link}'>LINK</a> abaixo.\n\n"
                )
            await asyncio.sleep(10)
    
if __name__ == "__main__":
    try:
        exe = NotifyOfferBot()
        asyncio.run(exe.envios_telegram(parse_mode="HTML"))
    except Exception as e:
        print(f"Erro na execução: {e}")
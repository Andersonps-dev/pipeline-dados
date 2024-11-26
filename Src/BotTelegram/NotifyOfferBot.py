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

    async def enviar_telegram_message(self, text):
        await self.bot.send_message(chat_id=self.CHAT_ID, text=text, message_thread_id=self.TOPIC_ID, parse_mode="HTML")

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
            vendido_por = i[4] if i[4] != None else "-"
            preco_antigo = i[7]
            preco_novo = i[8]
            porcentagem_desconto = i[9]
            detalhe_envio = i[10] if i[10] != None else "-"
            detalhe_envio_2 = i[11] if i[10] != None else "-"

            mensagem = (
                f"<b>🌟 {titulo} 🌟</b>\n\n"  # Título estilizado
                f"<i>✨ Oferta imperdível para você!</i>\n\n"
                f"🔥 <b>Por apenas:</b> <b>R$ {preco_novo}</b> 🔥\n\n"
                f"🔖 <b>Preço antigo:</b> R$ {preco_antigo}\n"
                f"✅ <b>Desconto incrível de:</b> {porcentagem_desconto}%\n\n"
                f"📦 <b>Observação de venda:</b>\n"
                f"➡️ {detalhe_envio}\n"
                f"➡️ {detalhe_envio_2}\n\n"
                f"🏬 <b>Vendido por:</b> {vendido_por}\n\n"
                f"🛒 <b>Garanta já o seu acessando o link abaixo:</b>\n"
                f"<a href='{link}'>🔗 Clique aqui para comprar</a>\n\n"
                f"⚡ <i>Corra, pois as ofertas podem acabar a qualquer momento!</i> ⚡"
            )

            await self.enviar_telegram_message(mensagem)
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        exe = NotifyOfferBot()
        asyncio.run(exe.envios_telegram())
    except Exception as e:
        print(f"Erro na execução: {e}")
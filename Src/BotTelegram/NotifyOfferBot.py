from datetime import datetime
import requests
import time
import pandas as pd
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
import sqlite3
from tabulate import tabulate

class NotifyOfferBot:
    def __init__(self):
        load_dotenv()
        self.__estancia_bot()

    def __estancia_bot(self):
        self.TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

        self.bot = Bot(token=self.TOKEN)

    async def enviar_telegram_message(self, text, topic_id):
        await self.bot.send_message(chat_id=self.CHAT_ID, text=text, message_thread_id=topic_id, parse_mode="HTML")

    def criar_conexao_sqlite3(self, db_name):
        conn = sqlite3.connect(db_name)
        return conn    
    
    def filtro_envios_principais(self, tabela):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT *, (preco_anterior-preco_atual) as desconto_reais FROM {tabela} WHERE porcentagem_desconto >= 40 or desconto_reais >= 600 ORDER BY porcentagem_desconto DESC LIMIT 100")
        resultado = cursor.fetchall()

        cursor.close()
        return resultado

    def salvar_consulta_anterior(self, tabela_atual, tabela_anterior):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        # Realiza a consulta
        cursor.execute(f"""
            SELECT *,
                (preco_anterior - preco_atual) AS desconto_reais 
            FROM {tabela_atual} 
            WHERE porcentagem_desconto >= 40 OR desconto_reais >= 600 
            ORDER BY porcentagem_desconto DESC 
            LIMIT 100
        """)
        resultado = cursor.fetchall()

        # Cria a nova tabela, se necessário
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {tabela_anterior} (
                highlight TEXT,
                titulo TEXT,
                link TEXT,
                vendido_por TEXT,
                nota REAL,
                total_avaliacoes INTEGER,
                preco_anterior REAL,
                preco_atual REAL,
                porcentagem_desconto REAL,
                detalhe_envio TEXT,
                detalhe_envio_2 TEXT,
                data_coleta TEXT,
                desconto_reais REAL
            )
        """)

    # Insere os dados na tabela
        for row in resultado:
            cursor.execute(f"""
                INSERT INTO {tabela_anterior} (
                    highlight, titulo, link, vendido_por, nota, total_avaliacoes, 
                    preco_anterior, preco_atual, porcentagem_desconto, detalhe_envio, 
                    detalhe_envio_2, data_coleta, desconto_reais
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

        conn.commit()
        cursor.close()
        conn.close()

    def verificar_itens_novos(self):
        pass

    def filtro_envios_reservas(self):
        pass

    async def envios_telegram(self, tabela, topic_id):
        for i in self.filtro_envios_principais(tabela):
            highlight = i[0] if i[0] != None else "-"
            titulo = i[1]
            link = i[2]
            vendido_por = i[3] if i[3] != None else "-"
            preco_antigo = i[6]
            preco_novo = i[7]
            porcentagem_desconto = i[8]
            detalhe_envio = i[9] if i[9] != None else "-"
            detalhe_envio_2 = i[10] if i[10] != None else "-"

            mensagem = (
                f"<b>🌟 {titulo} 🌟</b>\n\n"
                f"<i>✨ Oferta imperdível para você! {highlight} ✨</i>\n\n"
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

            await self.enviar_telegram_message(mensagem, topic_id)
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        exe = NotifyOfferBot()
        # asyncio.run(exe.envios_telegram("dados_games", "2"))
        # asyncio.run(exe.envios_telegram("dados_casa_moveis_decoracao", "4"))
        # exe.salvar_consulta_anterior("dados_games", "dados_games_anterior")
    except Exception as e:
        print(f"Erro na execução: {e}")
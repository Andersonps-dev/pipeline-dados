from datetime import datetime
import requests
import time
import pandas as pd
import asyncio
from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.error import TimedOut, RetryAfter
import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
import sqlite3
from tabulate import tabulate
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import *

class NotifyOfferBot:
    def __init__(self):
        
        super().__init__()
        
        load_dotenv()
        self.estancia_bot()

        self.lote_tamanho = LOTE_TAMANHO
        self.tempo_intervalo_lote = TEMPO_INTERVALO_LOTE
        self.relevancia = RELEVANCIA

    def estancia_bot(self):
        
        self.TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

        self.bot = Bot(token=self.TOKEN, request=HTTPXRequest(connect_timeout=10.0, read_timeout=15.0))

    async def enviar_telegram_message(self, text):
            try:
                await self.bot.send_message(
                    chat_id=self.CHAT_ID,
                    text=text,
                    # topic_id=topic_id
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}") 

    def criar_conexao_sqlite3(self, db_name):
        conn = sqlite3.connect(db_name)
        return conn    
    
    def filtro_tabelas(self, tabela):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()
    
        where_clause = " OR ".join(["relevancia = ?" for _ in self.relevancia])

        query = f"SELECT * FROM {tabela} WHERE {where_clause}"
        cursor.execute(query, self.relevancia)
        
        resultado = cursor.fetchall()

        resultado = sorted(resultado, key=lambda x: x[16])

        resultado = [(i, *row) for i, row in enumerate(resultado, start=1)]

        return resultado
    
    async def enviar_menssagem_em_lotes(self, fila):
        lote_tamanho = self.lote_tamanho
        intervalo_lote = self.tempo_intervalo_lote

        self.estancia_bot()
        
        try:
            for i in range(0, len(fila), lote_tamanho):
                lote = fila[i:i + lote_tamanho]

                for mensagem_dados in lote:
                    # topic_id = mensagem_dados[13]
                    highlight = mensagem_dados[1] if mensagem_dados[1] else ""
                    titulo = mensagem_dados[2]
                    link = mensagem_dados[3]
                    vendido_por = mensagem_dados[4] if mensagem_dados[4] else "-"
                    preco_antigo = mensagem_dados[7]
                    preco_novo = mensagem_dados[8]
                    porcentagem_desconto = mensagem_dados[9]
                    imagem = mensagem_dados[12]

                    mensagem = (
                        f"<b>🌟 {titulo} <a href='{imagem}' style=>.</a>🌟</b>\n\n"
                        f"<i>✨Oferta imperdível para você! {highlight}✨</i>\n\n"
                        f"🔥 <b>Por apenas:</b> <b>R$ {preco_novo}</b> 🔥\n\n"
                        f"🔖 <b>Preço antigo:</b> R$ {preco_antigo} ({porcentagem_desconto}% OFF ❌)\n"
                        f"🏬 <b>Vendido por:</b> {vendido_por}\n\n"
                        f"🛒 <b>Garanta já o seu acessando o link abaixo:</b>\n"
                        f"<a href='{link}'>🔗 Clique aqui para comprar</a>\n\n"
                    )
                    await self.enviar_telegram_message(mensagem)
                    await asyncio.sleep(20)

                print(f"Lote {i // lote_tamanho + 1} enviado. Aguardando {intervalo_lote} segundos antes do próximo lote...")
                await asyncio.sleep(intervalo_lote)
        finally:
            await self.bot.close()

if __name__ == "__main__":
    try:
        exe = NotifyOfferBot()
        exe.filtro_tabelas("dados_casa_moveis_decoracao")
        # async def main():
        #     await asyncio.gather(
        #         exe.enviar_menssagem_em_lotes(exe.filtro_tabelas("dados_casa_moveis_decoracao")),
        #         exe.enviar_menssagem_em_lotes(exe.filtro_tabelas("dados_games"))
        #     )
        # asyncio.run(main())
    except Exception as e:
        print(f"Erro na execução: {e}")
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
        
        self.limit_sql = LIMIT_SQL

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
    
    def filtro_envios(self, tabela, porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=None):
        
        limit_query_sql = limit_sql if limit_sql is not None else self.limit_sql
        
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT *, (preco_anterior-preco_atual) as desconto_reais FROM {tabela} WHERE porcentagem_desconto >= {porcentagem_maior_igual} AND porcentagem_desconto <= {porcentagem_menor} OR desconto_reais >= {desconto_reais} ORDER BY porcentagem_desconto DESC LIMIT {limit_query_sql}")
        resultado = cursor.fetchall()
        resultado = [(i, *row) for i, row in enumerate(resultado, start=1)]

        return resultado
    
    def salvar_dados_antigos(self, tabela_atual, tabela_anterior,porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=None):
        
        limit_query_sql = limit_sql if limit_sql is not None else self.limit_sql
        
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        resultado = self.filtro_envios(tabela_atual, porcentagem_maior_igual, porcentagem_menor, desconto_reais, limit_sql=limit_query_sql)
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {tabela_anterior} (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                highlight TEXT,
                titulo TEXT,
                link TEXT,
                vendido_por TEXT,
                nota TEXT,
                total_avaliacoes INTEGER,
                preco_anterior FLOAT,
                preco_atual FLOAT,
                porcentagem_desconto INTEGER,
                detalhe_envio TEXT,
                detalhe_envio_2 TEXT,
                data_coleta DATETIME,
                imagem TEXT,
                topico_de_envio TEXT,
                desconto_reais REAL
            )
        """)
        cursor.execute(f"DELETE FROM {tabela_anterior}")
        
        for row in resultado:
            cursor.execute(f"""
                INSERT INTO {tabela_anterior} (
                    Id,highlight, titulo, link, vendido_por, nota, total_avaliacoes, 
                    preco_anterior, preco_atual, porcentagem_desconto, detalhe_envio, 
                    detalhe_envio_2, imagem, data_coleta, topico_de_envio, desconto_reais
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

        conn.commit()
        cursor.close()
        conn.close()
        
    def filtro_envios_antigos(self, tabela):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {tabela}")
        resultado = cursor.fetchall()

        cursor.close()
        conn.close()
        
        return resultado
            
    def verificar_itens_novos(self, tabela, tabela_antiga):
        nova_coleta = self.filtro_envios(tabela)
        antiga_coleta = self.filtro_envios_antigos(tabela_antiga)

        novos_itens = []

        nome_itens = [item[2] for item in antiga_coleta]
        
        for item in nova_coleta:
            if item[2] not in nome_itens:
                novos_itens.append(item)

        return novos_itens
    
    def verificar_reducao_preco(self, tabela, tabela_antiga):
        nova_coleta = self.filtro_envios(tabela)
        antiga_coleta = self.filtro_envios_antigos(tabela_antiga)
        
        novos_precos = []
        
        antiga_coleta_dict = {item[2]: float(item[7].replace(',', '.')) for item in antiga_coleta}
        
        for item in nova_coleta:
            nome = item[1]
            preco_novo = float(item[7].replace(',', '.'))
            if nome in antiga_coleta_dict and preco_novo < antiga_coleta_dict[nome]:
                novos_precos.append(item)

        return novos_precos
    
    async def enviar_menssagem_em_lotes(self, fila, lote_tamanho=5, intervalo_lote=100):
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
                    detalhe_envio = mensagem_dados[10] if mensagem_dados[10] else "-"
                    detalhe_envio_2 = mensagem_dados[11] if mensagem_dados[11] else "-"

                    mensagem = (
                        f"<b>🌟 {titulo} <a href='{imagem}' style=>.</a>🌟</b>\n\n"
                        f"<i>✨Oferta imperdível para você! {highlight}✨</i>\n\n"
                        f"🔥 <b>Por apenas:</b> <b>R$ {preco_novo}</b> 🔥\n\n"
                        f"🔖 <b>Preço antigo:</b> R$ {preco_antigo} ({porcentagem_desconto}% OFF ❌)\n"
                        f"🏬 <b>Vendido por:</b> {vendido_por}\n\n"
                        f"🛒 <b>Garanta já o seu acessando o link abaixo:</b>\n"
                        f"<a href='{link}'>🔗 Clique aqui para comprar</a>\n\n"
                    )

                    # Envie a mensagem
                    await self.enviar_telegram_message(mensagem)
                    await asyncio.sleep(20)

                print(f"Lote {i // lote_tamanho + 1} enviado. Aguardando {intervalo_lote} segundos antes do próximo lote...")
                await asyncio.sleep(intervalo_lote)
        finally:
            await self.bot.close()

if __name__ == "__main__":
    try:
        exe = NotifyOfferBot()
        async def main():
            await asyncio.gather(
                exe.enviar_menssagem_em_lotes(exe.filtro_envios("dados_casa_moveis_decoracao", limit_sql=3))
            )
        asyncio.run(main())
    except Exception as e:
        print(f"Erro na execução: {e}")
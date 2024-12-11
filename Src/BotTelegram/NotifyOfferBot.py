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
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class NotifyOfferBot:
    def __init__(self):
        load_dotenv()
        self.__estancia_bot()

    def __estancia_bot(self):
        self.TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

        self.bot = Bot(token=self.TOKEN)

    async def __enviar_telegram_message(self, text, topic_id):
        await self.bot.send_message(chat_id=self.CHAT_ID, text=text, message_thread_id=topic_id, parse_mode="HTML")

    def criar_conexao_sqlite3(self, db_name):
        conn = sqlite3.connect(db_name)
        return conn    
    
    def filtro_envios(self, tabela, porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=100):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT *, (preco_anterior-preco_atual) as desconto_reais FROM {tabela} WHERE porcentagem_desconto >= {porcentagem_maior_igual} AND porcentagem_desconto <= {porcentagem_menor} OR desconto_reais >= {desconto_reais} ORDER BY porcentagem_desconto DESC LIMIT {limit_sql}")
        resultado = cursor.fetchall()

        return resultado
    
    def salvar_dados_antigos(self, tabela_atual, tabela_anterior,porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=100):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        resultado = self.filtro_envios(tabela_atual, porcentagem_maior_igual, porcentagem_menor, desconto_reais, limit_sql)
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {tabela_anterior} (
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
                desconto_reais REAL
            )
        """)
        cursor.execute(f"DELETE FROM {tabela_anterior}")
        
        for row in resultado:
            cursor.execute(f"""
                INSERT INTO {tabela_anterior} (
                    highlight, titulo, link, vendido_por, nota, total_avaliacoes, 
                    preco_anterior, preco_atual, porcentagem_desconto, detalhe_envio, 
                    detalhe_envio_2, imagem, data_coleta, desconto_reais
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        return resultado
            
    def verificar_itens_novos(self, tabela, tabela_antiga):
        nova_coleta = self.filtro_envios(tabela)
        antiga_coleta = self.filtro_envios_antigos(tabela_antiga)

        novos_itens = []

        nome_itens = [item[1] for item in antiga_coleta]

        for item in nova_coleta:
            if item[1] not in nome_itens:
                novos_itens.append(item)

        return novos_itens
    
    def verificar_reducao_preco(self, tabela, tabela_antiga):
        nova_coleta = self.filtro_envios(tabela)
        antiga_coleta = self.filtro_envios_antigos(tabela_antiga)

        novos_precos = []

        antiga_coleta_dict = {item[1]: float(item[7].replace(',', '.')) for item in antiga_coleta}
        
        for item in nova_coleta:
            nome = item[1]
            preco_novo = float(item[7].replace(',', '.'))
            if nome in antiga_coleta_dict and preco_novo < antiga_coleta_dict[nome]:
                novos_precos.append(item)

        return novos_precos
    
    async def envios_telegram_todos_itens(self, tabela, topic_id, porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=100):
        for i in self.filtro_envios(tabela, porcentagem_maior_igual, porcentagem_menor, desconto_reais, limit_sql):
            highlight = i[0] if i[0] != None else ""
            titulo = i[1]
            link = i[2]
            vendido_por = i[3] if i[3] != None else "-"
            preco_antigo = i[6]
            preco_novo = i[7]
            porcentagem_desconto = i[8]
            imagem = i[11]
            detalhe_envio = i[9] if i[9] != None else "-"
            detalhe_envio_2 = i[10] if i[10] != None else "-"

            mensagem = (
                f"<b>🌟 {titulo} <a href='{imagem}' style=>.</a>🌟</b>\n\n"
                f"<i>✨Oferta imperdível para você! {highlight}✨</i>\n\n"
                f"🔥 <b>Por apenas:</b> <b>R$ {preco_novo}</b> 🔥\n\n"
                f"🔖 <b>Preço antigo:</b> R$ {preco_antigo} ({porcentagem_desconto}% OFF ❌)\n"
                f"🏬 <b>Vendido por:</b> {vendido_por}\n\n"
                f"🛒 <b>Garanta já o seu acessando o link abaixo:</b>\n"
                f"<a href='{link}'>🔗 Clique aqui para comprar</a>\n\n"
            )

            await self.__enviar_telegram_message(mensagem, topic_id)
            await asyncio.sleep(5)
    
    async def envios_telegram_novas_ofertas(self, tabela, tabela_antiga, topic_id):
        for i in self.verificar_itens_novos(tabela, tabela_antiga):
            highlight = i[0] if i[0] != None else "-"
            titulo = i[1]
            link = i[2]
            vendido_por = i[3] if i[3] != None else "-"
            preco_antigo = i[6]
            preco_novo = i[7]
            porcentagem_desconto = i[8]
            imagem = i[11]
            detalhe_envio = i[9] if i[9] != None else "-"
            detalhe_envio_2 = i[10] if i[10] != None else "-"

            mensagem = (
                f"<b>🌟 {titulo} <a href='{imagem}' style=>.</a>🌟</b>\n\n"
                f"<i> ✨ <b>NOVA</b> oferta imperdível para você! {highlight} ✨</i>\n\n"
                f"🔥 <b>Por apenas:</b> <b>R$ {preco_novo}</b> 🔥\n\n"
                f"🔖 <b>Preço antigo:</b> R$ {preco_antigo} ({porcentagem_desconto}% OFF ❌)\n"
                f"🏬 <b>Vendido por:</b> {vendido_por}\n\n"
                f"🛒 <b>Garanta já o seu acessando o link abaixo:</b>\n"
                f"<a href='{link}'>🔗 Clique aqui para comprar</a>\n\n"
            )

            await self.__enviar_telegram_message(mensagem, topic_id)
            await asyncio.sleep(5)
            
    async def envios_telegram_reducao_preco(self, tabela, tabela_antiga, topic_id):
        for i in self.verificar_reducao_preco(tabela, tabela_antiga):
            highlight = i[0] if i[0] != None else "-"
            titulo = i[1]
            link = i[2]
            vendido_por = i[3] if i[3] != None else "-"
            preco_antigo = i[6]
            preco_novo = i[7]
            porcentagem_desconto = i[8]
            imagem = i[11]
            detalhe_envio = i[9] if i[9] != None else "-"
            detalhe_envio_2 = i[10] if i[10] != None else "-"

            mensagem = (
                f"<b>🌟 {titulo} <a href='{imagem}' style=>.</a>🌟</b>\n\n"
                f"<i> ✨ <b>REDUÇÃO DE PREÇO</b> oferta imperdível para você! {highlight} ✨</i>\n\n"
                f"🔥 <b>Por apenas:</b> <b>R$ {preco_novo}</b> 🔥\n\n"
                f"🔖 <b>Preço antigo:</b> R$ {preco_antigo} ({porcentagem_desconto}% OFF ❌)\n"
                f"🏬 <b>Vendido por:</b> {vendido_por}\n\n"
                f"🛒 <b>Garanta já o seu acessando o link abaixo:</b>\n"
                f"<a href='{link}'>🔗 Clique aqui para comprar</a>\n\n"
            )
            
            await self.__enviar_telegram_message(mensagem, topic_id)
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        exe = NotifyOfferBot()
        async def main():
            await asyncio.gather(
                exe.envios_telegram_todos_itens("dados_casa_moveis_decoracao", "4"),
                # exe.envios_telegram_novas_ofertas("dados_casa_moveis_decoracao", "dados_casa_moveis_decoracao_tabela_anterior", "4"),
                # exe.envios_telegram_reducao_preco("dados_casa_moveis_decoracao", "dados_casa_moveis_decoracao_tabela_anterior", "4")
            )
        asyncio.run(main())
    except Exception as e:
        print(f"Erro na execução: {e}")
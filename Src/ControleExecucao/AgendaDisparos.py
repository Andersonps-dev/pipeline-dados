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
import schedule

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Transformacao.main import Transformacao
from BotTelegram.NotifyOfferBot import NotifyOfferBot
from ControleExecucao.ExecutarColeta import ExecutarColeta

class ScheduleJob(ExecutarColeta):
    def __init__(self):
        super().__init__()
        self.conn = self.criar_conexao_sqlite3("dados_coletados.db")
    
    def coletar_dados(self):
        self.executar_scrapy("ofertas_casa_moveis_decoracao", "dados_casa_moveis_decoracao")
        self.executar_scrapy("ofertas_games", "dados_games")
        
    def tratar_dados(self):
        self.tratar_base(conn=self.conn, nome_arquivo="dados_casa_moveis_decoracao.jsonl", nome_tabela_bd="dados_casa_moveis_decoracao")
        self.tratar_base(conn=self.conn, nome_arquivo="dados_games.jsonl", nome_tabela_bd="dados_games")
        self.conn.close()
        
    def fila_bases(self):
        bases = [self.filtro_envios("dados_casa_moveis_decoracao"), self.filtro_envios("dados_games")]
        fila = []
        for i in bases:
            fila.append(i)
            
        return fila
    
    def enviar_mensagens_iniciais(self):
        async def main():
            await asyncio.gather(
                self.envios_telegram_todos_itens("dados_casa_moveis_decoracao", "4")
            )
        asyncio.run(main())
        
    def disparo_inicial(self):
        schedule.every().day.at("06:00").do(self.coletar_dados)
        schedule.every().day.at("06:00").do(self.tratar_dados)

    def disparo_periodico(self):
        pass
    
if __name__ == "__main__":
    exe = ScheduleJob()
    exe.disparo_inicial()
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
        self.estancia_bot()
        
        self.grupos = {
            "ofertas_casa_moveis_decoracao": "4",
            "ofertas_games": "2"
        }
        
        self.bases_para_envios_iniciais = ["dados_casa_moveis_decoracao", "dados_games"]
                                                         
    def coletar_dados(self):
        self.executar_scrapy("ofertas_casa_moveis_decoracao", "dados_casa_moveis_decoracao")
        self.executar_scrapy("ofertas_games", "dados_games")
        
    def tratar_dados(self):
        self.tratar_base(conn=self.conn, nome_arquivo="dados_casa_moveis_decoracao.jsonl", nome_tabela_bd="dados_casa_moveis_decoracao", topic_id=self.grupos["ofertas_casa_moveis_decoracao"])
        self.tratar_base(conn=self.conn, nome_arquivo="dados_games.jsonl", nome_tabela_bd="dados_games", topic_id=self.grupos["ofertas_games"])
        self.conn.close()
        
    def fila_bases_iniciais(self):
        bases_envios_iniciais = [self.filtro_envios(base) for base in self.bases_para_envios_iniciais]
        
        fila = []
        for i in bases_envios_iniciais:
            fila.extend(i) 

        fila_ordenada = sorted(fila, key=lambda x: x[0])

        return fila_ordenada
    
    def fila_itens_novos(self):
        bases_envios_iniciais = [self.verificar_itens_novos(base, base + "_tabela_anterior") for base in self.bases_para_envios_iniciais]
        
        fila = []
        for i in bases_envios_iniciais:
            fila.extend(i) 

        fila_ordenada = sorted(fila, key=lambda x: x[0])

        return fila_ordenada

    def envios_iniciais(self):
        async def main():
            fila = self.fila_bases_iniciais()
            await asyncio.gather(
                self.enviar_menssagem_telegram(fila)
            )
        asyncio.run(main())
    
    def envios_periodicos(self):
        async def main():
            fila = self.fila_itens_novos()
            await asyncio.gather(
                self.enviar_menssagem_telegram(fila)
            )
        asyncio.run(main())
        
    def disparo_inicial(self):
        horario = "06:00"
        schedule.every().day.at(horario).do(self.coletar_dados)
        schedule.every().day.at(horario).do(self.tratar_dados)
        schedule.every().day.at(horario).do(self.envios_iniciais)

    def disparo_periodico(self):
        pass
    
if __name__ == "__main__":
    exe = ScheduleJob()
    # exe.coletar_dados()
    # exe.tratar_dados()
    exe.fila_itens_novos()
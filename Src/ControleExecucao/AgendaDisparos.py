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
from ExecutarColeta import ExecutarColeta

from config import *

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

        self.limit_sql = LIMIT_SQL
                                                         
    def coletar_dados(self):
        self.executar_scrapy("ofertas_casa_moveis_decoracao", "dados_casa_moveis_decoracao")
        self.executar_scrapy("ofertas_games", "dados_games")
        
    def tratar_dados(self):
        self.tratar_base(conn=self.conn, nome_arquivo="dados_casa_moveis_decoracao.jsonl", nome_tabela_bd="dados_casa_moveis_decoracao", topic_id=self.grupos["ofertas_casa_moveis_decoracao"])
        self.tratar_base(conn=self.conn, nome_arquivo="dados_games.jsonl", nome_tabela_bd="dados_games", topic_id=self.grupos["ofertas_games"])
        self.conn.close()
        
    def fila_bases_iniciais(self,  porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=None):

        limit_query_sql = limit_sql if limit_sql is not None else self.limit_sql

        bases_envios_iniciais = [self.filtro_envios(base, porcentagem_maior_igual, porcentagem_menor, desconto_reais, limit_sql=limit_query_sql) for base in self.bases_para_envios_iniciais]
        
        fila = []

        if len(bases_envios_iniciais) == 0:
            pass
        else:
            for i in bases_envios_iniciais:
                fila.extend(i)

        fila_ordenada = sorted(fila, key=lambda x: x[0])

        return fila_ordenada
    
    def fila_itens_novos(self):
        bases_envios_iniciais = [self.verificar_itens_novos(base, base + "_tabela_anterior") for base in self.bases_para_envios_iniciais]
        
        fila = []

        if len(bases_envios_iniciais) > 0:
            for i in bases_envios_iniciais:
                fila.extend(i)            
        else:
            pass
            
        fila_ordenada = sorted(fila, key=lambda x: x[0])

        return fila_ordenada

    def fila_itens_reducao_preco(self):
        bases_envios_iniciais = [self.verificar_reducao_preco(base, base + "_tabela_anterior") for base in self.bases_para_envios_iniciais]

        fila = []

        if len(bases_envios_iniciais) > 0:
            for i in bases_envios_iniciais:
                fila.extend(i)
        else:
            pass

        fila_ordenada = sorted(fila, key=lambda x: x[0])

        return fila_ordenada
    
    def envios_iniciais(self, porcentagem_maior_igual=40, porcentagem_menor=100, desconto_reais=600, limit_sql=None):

        limit_query_sql = limit_sql if limit_sql is not None else self.limit_sql

        async def main():
            fila = self.fila_bases_iniciais(porcentagem_maior_igual, porcentagem_menor, desconto_reais, limit_sql=limit_query_sql)
            await asyncio.gather(
                self.enviar_menssagem_em_lotes(fila)
            )
        asyncio.run(main())
    
    def envios_itens_reducao_preco_e_novos(self):
        fila_novos = self.fila_itens_novos()
        fila_reducao = self.fila_itens_reducao_preco()
        
        fila_novos.extend(fila_reducao)
        
        async def main():
            fila_geral = sorted(fila_novos, key=lambda x: x[0])
            await asyncio.gather(
                self.enviar_menssagem_em_lotes(fila_geral)
            )
            await self.bot.close()
        asyncio.run(main())

    def execucao_completa(self, horario):
            self.coletar_dados()
            self.tratar_dados()

            if horario == PRIMEIRO_HORARIO:
                print("Iniciando os envios primeiro horario...")
                self.envios_iniciais()
                print("Fim dos envios primeiro horario...")
                
            elif horario == SEGUNDO_HORARIO:
                print("Iniciando os envios segundo horario...")
                if len(self.fila_itens_novos()) + len(self.fila_itens_reducao_preco()) < 20:
                    self.envios_itens_reducao_preco_e_novos()
                    self.envios_iniciais(porcentagem_maior_igual=35, porcentagem_menor=40, desconto_reais=400, limit_sql=10)
                else:
                    self.envios_itens_reducao_preco_e_novos()
                print("Fim dos envios segundo horario...")
                    
            elif horario == TERCEIRO_HORARIO:
                print("Iniciando os envios terceiro horario...")
                if len(self.fila_itens_novos()) + len(self.fila_itens_reducao_preco()) < 20:
                    self.envios_itens_reducao_preco_e_novos()
                    self.envios_iniciais(porcentagem_maior_igual=30, porcentagem_menor=35, desconto_reais=200, limit_sql=10)
                else:
                    self.envios_itens_reducao_preco_e_novos()
                print("Fim dos envios terceiro horario...")

    def configurar_agendador(self):
        horarios = [PRIMEIRO_HORARIO, SEGUNDO_HORARIO, TERCEIRO_HORARIO]
        for horario in horarios:
            schedule.every().day.at(horario).do(self.execucao_completa, horario=horario)
            
    def executar_agendador(self):
        self.configurar_agendador()
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    agenda = ScheduleJob()
    agenda.executar_agendador()
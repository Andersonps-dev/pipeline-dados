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

        self.categorias = CATEGORIAS
        self.relevancia = RELEVANCIA
        self.lote_tamanho = LOTE_TAMANHO
        self.tempo_intervalo_lote = TEMPO_INTERVALO_LOTE

        self.criar_tabela_fila_anterior()
                                                         
    def coletar_dados(self):
        fila_atual = self.fila_tabelas()
        self.salvar_fila_anterior(fila_atual)
        
        self.executar_scrapy("ofertas_casa_moveis_decoracao", "dados_casa_moveis_decoracao")
        self.executar_scrapy("ofertas_games", "dados_games")
        
    def tratar_dados(self):
        self.tratar_base(conn=self.conn, nome_arquivo="dados_casa_moveis_decoracao.jsonl", nome_tabela_bd="dados_casa_moveis_decoracao", topic_id=self.grupos["ofertas_casa_moveis_decoracao"])
        self.tratar_base(conn=self.conn, nome_arquivo="dados_games.jsonl", nome_tabela_bd="dados_games", topic_id=self.grupos["ofertas_games"])
        self.conn.close()
        
    def fila_tabelas(self):
        bases_envios_iniciais = [self.filtro_tabelas(base) for base in self.categorias]
        
        fila = []

        for i in bases_envios_iniciais:
            fila.extend(i)

        fila_ordenada = sorted(fila, key=lambda x: x[0])

        return fila_ordenada

    def criar_tabela_fila_anterior(self):
        query = """
        CREATE TABLE IF NOT EXISTS fila_anterior (
            id INTEGER,
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
            imagem TEXT,
            data_coleta TEXT,
            topico_de_envio TEXT,
            desconto_reais REAL,
            pontuacao INTEGER,
            relevancia TEXT
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def salvar_fila_anterior(self, fila):
        self.conn.execute("DELETE FROM fila_anterior")
        self.conn.commit()

        query = """
        INSERT INTO fila_anterior (
            id, highlight, titulo, link, vendido_por, nota, total_avaliacoes, preco_anterior,
            preco_atual, porcentagem_desconto, detalhe_envio, detalhe_envio_2, imagem,
            data_coleta, topico_de_envio, desconto_reais, pontuacao, relevancia
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.conn.executemany(query, fila)
        self.conn.commit()

    def recuperar_fila_anterior(self):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        query = "SELECT id, titulo, relevancia FROM fila_anterior;"
        cursor = conn.execute(query)
        dados = cursor.fetchall()
        conn.close()
        return dados
    
    def comparar_filas(self):
            fila_anterior = self.recuperar_fila_anterior()
            fila_atual = self.fila_tabelas()
            mudancas = []

            mapa_fila_anterior = {item[1]: item for item in fila_anterior}

            for item in fila_atual:
                titulo, relevancia = item[2], item[16]
                if titulo not in mapa_fila_anterior or mapa_fila_anterior[titulo][2] != relevancia:
                    mudancas.append(item)

            return mudancas
    
    def envios_mensagens(self, itens=None):
        async def main(itens):
            if itens is None:
                itens = self.fila_tabelas()
            await asyncio.gather(
                self.enviar_menssagem_em_lotes(itens)
            )
        asyncio.run(main(itens))

    def executar_tarefas(self):
        while True:
            self.coletar_dados()
            self.tratar_dados()
            mudancas = self.comparar_filas()
            
            if mudancas:
                self.envios_mensagens(mudancas)
            else:
                time.sleep(3600)

if __name__ == "__main__":
    agenda = ScheduleJob()
    agenda.executar_tarefas()
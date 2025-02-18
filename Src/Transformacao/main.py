import pandas as pd
import sqlite3
from datetime import datetime
import requests
import time
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
from tabulate import tabulate
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from BotTelegram.NotifyOfferBot import *
from config import *

class Transformacao(NotifyOfferBot):
    def __init__(self):
        load_dotenv()

        self.palavras_chaves = PALAVRAS_CHAVES

        self.pasta_dados = r'..\pipeline-dados\Dados'
    
    def tratar_base(self, conn=None, nome_arquivo=None, nome_tabela_bd=None, nome_bd='dados_coletados.db', topic_id=None):
        caminho = os.path.join(self.pasta_dados, nome_arquivo)
        
        df = pd.read_json(caminho, lines=True)
        
        # Conversão de tipos
        df["preco_anterior"] = df["preco_anterior"].astype(str)
        df["fracao_preco_anterior"] = df["fracao_preco_anterior"].astype(str)
        df["preco_atual"] = df["preco_atual"].astype(str)
        df["fracao_preco_atual"] = df["fracao_preco_atual"].astype(str)

        # Função para limpar números
        def limpar_numero(valor):
            if pd.isnull(valor) or valor == '':
                return 0
            return int(str(valor).replace('.', '').replace(',', ''))

        # Substituição de valores None
        colunas_substituir_none = ['preco_anterior', 'fracao_preco_anterior', 'preco_atual', 'fracao_preco_atual']
        df[colunas_substituir_none] = df[colunas_substituir_none].replace([None, 'None', ''], 0)

        # Aplicação da função de limpeza
        df["preco_anterior"] = df["preco_anterior"].apply(limpar_numero)
        df["fracao_preco_anterior"] = df["fracao_preco_anterior"].apply(limpar_numero)
        df["preco_atual"] = df["preco_atual"].apply(limpar_numero)
        df["fracao_preco_atual"] = df["fracao_preco_atual"].apply(limpar_numero)

        # Concatenação e conversão para float
        df['preco_anterior'] = df["preco_anterior"].astype(str) + "," + df["fracao_preco_anterior"].astype(str)
        df['preco_atual'] = df["preco_atual"].astype(str) + "," + df["fracao_preco_atual"].astype(str)
        df['preco_anterior'] = df['preco_anterior'].str.replace(',', '.').astype(float)
        df['preco_atual'] = df['preco_atual'].str.replace(',', '.').astype(float)

        # Remoção de colunas desnecessárias
        df = df.drop(columns=['fracao_preco_anterior', 'fracao_preco_atual'])

        # Extração de porcentagem de desconto
        df['porcentagem_desconto'] = df['porcentagem_desconto'].str.extract('(\d+)').fillna(0).astype(int)

        # Ordenação e remoção de duplicatas
        df = df.sort_values('porcentagem_desconto', ascending=True)
        df = df.drop_duplicates(subset=['titulo'], keep='last')

        # Adição de colunas adicionais
        df['data_coleta'] = datetime.now()
        df['topico_de_envio'] = f"{topic_id}"
        df['desconto_reais'] = df['preco_anterior'] - df['preco_atual']

        # Função para calcular pontuação
        def calcular_pontuacao(row, lojas_vistas):
            pontuacao = 0

            # Regras baseadas em porcentagem de desconto
            regras_porcentagem = [
                {"condicao": lambda r: r["porcentagem_desconto"] >= 50, "pontuacao": 5},
                {"condicao": lambda r: r["porcentagem_desconto"] >= 45, "pontuacao": 4},
                {"condicao": lambda r: r["porcentagem_desconto"] >= 40, "pontuacao": 3},
                {"condicao": lambda r: r["porcentagem_desconto"] >= 35, "pontuacao": 2},
                {"condicao": lambda r: r["porcentagem_desconto"] >= 25, "pontuacao": 1},
            ]

            # Regras baseadas em desconto em reais
            regras_reais = [
                {"condicao": lambda r: r["desconto_reais"] > 1000 and r["porcentagem_desconto"] < 50, "pontuacao": 5},
                {"condicao": lambda r: r["desconto_reais"] > 600 and r["porcentagem_desconto"] < 40, "pontuacao": 4},
                {"condicao": lambda r: r["desconto_reais"] > 300 and r["porcentagem_desconto"] < 20, "pontuacao": 3},
                {"condicao": lambda r: r["desconto_reais"] > 100 and r["porcentagem_desconto"] < 10, "pontuacao": 3},
            ]

            # Regras para colunas específicas
            regras_gerais = [
                {"condicao": lambda r: pd.notna(r["highlight"]), "pontuacao": 2},
                {"condicao": lambda r: pd.notna(r["vendido_por"]), "pontuacao": 1},
                {"condicao": lambda r: pd.notna(r["detalhe_envio"]) or pd.notna(r["detalhe_envio_2"]), "pontuacao": 1},
            ]

            # Penalidade para "vendido_por" em lojas vistas
            penalidade_vendido_por = {
                "condicao": lambda r: pd.notna(r["vendido_por"]) and r["vendido_por"] in lojas_vistas and r["vendido_por"] != "Por Mercado Livre",
                "pontuacao": -3
            }

            # Aplicar regras baseadas em porcentagem
            for regra in regras_porcentagem:
                if regra["condicao"](row):
                    pontuacao += regra["pontuacao"]

            # Aplicar regras baseadas em desconto em reais
            for regra in regras_reais:
                if regra["condicao"](row):
                    pontuacao += regra["pontuacao"]

            # Aplicar regras gerais
            for regra in regras_gerais:
                if regra["condicao"](row):
                    pontuacao += regra["pontuacao"]

            # Aplicar penalidade
            if penalidade_vendido_por["condicao"](row):
                pontuacao += penalidade_vendido_por["pontuacao"]

            # Adicionar loja a lojas vistas
            if pd.notna(row["vendido_por"]):
                lojas_vistas.add(row["vendido_por"])

            # Palavras-chave no título
            for palavra in self.palavras_chaves:
                if palavra in row['titulo']:
                    pontuacao += 2

            return pontuacao

        # Aplicação da função de pontuação
        lojas_vistas = set()
        df["pontuacao"] = df.apply(calcular_pontuacao, axis=1, lojas_vistas=lojas_vistas)

        # Classificação de relevância
        def classificar_relevancia(pontuacao):
            if pontuacao >= 8:
                return "1"
            elif pontuacao >= 6:
                return "2"
            elif pontuacao >= 5:
                return "3"
            elif pontuacao >= 2:
                return "4"
            else:
                return "5"

        df["relevancia"] = df["pontuacao"].apply(classificar_relevancia)

        # Filtragem e salvamento no banco de dados
        df = df[df['porcentagem_desconto'] != 0]
        df.to_sql(nome_tabela_bd, criar_conexao_sqlite3(nome_bd), if_exists='replace', index=False)

    def criar_conexao_sqlite3(self, db_name):
        conn = sqlite3.connect(db_name)
        return conn
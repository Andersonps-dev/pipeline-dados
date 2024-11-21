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
from telegram import Bot
from tabulate import tabulate

class Transformacao:
    def __init__(self):
        load_dotenv()
        self.POSTGRES_DB = os.getenv("POSTGRES_DB")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT")

        self.pasta_dados = r'..\pipeline-dados\Dados'
    
    def tratar_base(self, conn=None, nome_arquivo=None, nome_tabela_bd=None, nome_bd='dados_coletados.db'):
        caminho = os.path.join(self.pasta_dados, nome_arquivo)
        
        df = pd.read_json(caminho, lines=True, dtype={"preco_anterior": str, "fracao_preco_anterior":str, "preco_atual":str, "fracao_preco_atual":str})
        def limpar_numero(valor):
            if pd.isnull(valor):
                return valor
            return int(str(valor).replace('.', '').replace(',', ''))

        colunas_substituir_none = ['preco_anterior', 'fracao_preco_anterior', 'preco_atual', 'fracao_preco_atual']
        df[colunas_substituir_none] = df[colunas_substituir_none].replace(['None', None], 0)

        df["preco_anterior"] = df["preco_anterior"].apply(limpar_numero)
        df["fracao_preco_anterior"] = df["fracao_preco_anterior"].apply(limpar_numero)
        df["preco_atual"] = df["preco_atual"].apply(limpar_numero)
        df["fracao_preco_atual"] = df["fracao_preco_atual"].apply(limpar_numero)
        
        df['preco_anterior'] = df["preco_anterior"].astype(str) + "," + df["fracao_preco_anterior"].astype(str)
        df['preco_atual'] = df["preco_atual"].astype(str) + "," + df["fracao_preco_atual"].astype(str)
        
        df = df.drop(columns=['fracao_preco_anterior', 'fracao_preco_atual'])
        
        df['data_coleta']  = datetime.now()

        self.criar_tabela(conn, nome_tabela_bd)
        df.to_sql(nome_tabela_bd, self.criar_conexao_sqlite3(nome_bd), if_exists='append', index=False)

    def criar_conexao_sqlite3(self, db_name):
        conn = sqlite3.connect(db_name)
        return conn

    def criar_tabela(self, conn, nome_tabela):
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {nome_tabela} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                highlight TEXT,
                titulo TEXT,
                link TEXT,
                vendido_por TEXT,
                nota TEXT,
                total_avaliacoes INTEGER,
                preco_anterior FLOAT,
                preco_atual FLOAT,
                porcentagem_desconto TEXT,
                detalhe_envio TEXT,
                detalhe_envio_2 TEXT,
                data_coleta DATETIME
            )
        ''')
        conn.commit()

    def criar_conexao_postgres(self):
        try:
            conn = psycopg2.connect(
                dbname=self.POSTGRES_DB,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT
            )
            return conn
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
    
    def testar_conexao_postgres(self):
        conn = self.criar_conexao_postgres()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                print("Conexão bem-sucedida, teste retornou:", result)
            except psycopg2.Error as e:
                print(f"Erro ao executar o teste de conexão: {e}")
            finally:
                conn.close()
        else:
            print("Conexão falhou.")
        
    def executor(self):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        self.tratar_base(conn=conn, nome_arquivo="dados_games.jsonl", nome_tabela_bd="dados_games")
        self.tratar_base(conn=conn, nome_arquivo="dados_casa_moveis_decoracao.jsonl", nome_tabela_bd="dados_casa_moveis_decoracao")
    
exe = Transformacao()
exe.executor()
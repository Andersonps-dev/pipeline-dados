import pandas as pd
import sqlite3
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

class Transformacao:
    def __init__(self):
        load_dotenv()
        self.POSTGRES_DB = os.getenv("POSTGRES_DB")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT")

        self.pasta_dados = r'..\pipeline-dados\Dados'

    def criar_conexao(self):
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
    
    def testar_conexao(self):
        conn = self.criar_conexao()
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
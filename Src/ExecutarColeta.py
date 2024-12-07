import subprocess
import os
import sys

from Transformacao.main import Transformacao

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ExecutorDeScripts(Transformacao):
    def __init__(self):
        super().__init__()
        
        self.diretorio_principal = os.path.abspath(os.getcwd())
        self.python_venv = os.path.join(self.diretorio_principal, ".venv", "Scripts", "python.exe")

    def salvar_dados_antigos(self, tabela_atual, tabela_anterior):
        conn = self.criar_conexao_sqlite3("dados_coletados.db")
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT *,
                (preco_anterior - preco_atual) AS desconto_reais 
            FROM {tabela_atual}
            WHERE porcentagem_desconto >= 40 OR desconto_reais >= 600
            ORDER BY porcentagem_desconto DESC 
            LIMIT 100
        """)
        resultado = cursor.fetchall()
        
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
                desconto_reais REAL
            )
        """)
        cursor.execute(f"DELETE FROM {tabela_anterior}")
        
        for row in resultado:
            cursor.execute(f"""
                INSERT INTO {tabela_anterior} (
                    highlight, titulo, link, vendido_por, nota, total_avaliacoes, 
                    preco_anterior, preco_atual, porcentagem_desconto, detalhe_envio, 
                    detalhe_envio_2, data_coleta, desconto_reais
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

        conn.commit()
        cursor.close()
        conn.close()
    
    def executar_scrapy(self, coleta, nome_arquivo):
        self.salvar_dados_antigos(nome_arquivo, f"{nome_arquivo}_tabela_anterior")
        try:
            scrapy_dir = os.path.join(self.diretorio_principal, "Src", "Coleta", "Coleta", "spiders")
            os.chdir(scrapy_dir)
            comando = f"scrapy crawl {coleta} -O ..\..\..\..\Dados\{nome_arquivo}.jsonl"
            print(f"Executando: {comando}")
            subprocess.run(comando, shell=True, check=True)
        finally:
            os.chdir(self.diretorio_principal)

if __name__ == "__main__":
    executor = ExecutorDeScripts()
    executor.executar_scrapy("ofertas_casa_moveis_decoracao", "dados_casa_moveis_decoracao")
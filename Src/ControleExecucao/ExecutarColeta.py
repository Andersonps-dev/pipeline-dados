import subprocess
import os
import sys
from scrapy.crawler import CrawlerProcess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Transformacao.main import Transformacao
from BotTelegram.NotifyOfferBot import NotifyOfferBot

from config import *

class ExecutarColeta(Transformacao, NotifyOfferBot):
    def __init__(self):
        super().__init__()
        
        self.diretorio_principal = os.path.abspath(os.getcwd())
        self.python_venv = os.path.join(self.diretorio_principal, ".venv", "Scripts", "python.exe")
    
    def executar_scrapy(self, coleta, nome_arquivo):
        try:
            scrapy_dir = os.path.join(self.diretorio_principal, "Src", "Coleta", "Coleta", "spiders")
            os.chdir(scrapy_dir)
            comando = f"scrapy crawl {coleta} -O Dados\{nome_arquivo}.jsonl"
            print(f"Executando: {comando}")
            subprocess.run(comando, shell=True, check=True)
        finally:
            os.chdir(self.diretorio_principal)

if __name__ == "__main__":
    try:
        exe = ExecutarColeta()
        exe.executar_scrapy("ofertas_games", "dados_games")
        exe.executar_scrapy("ofertas_casa_moveis_decoracao", "dados_casa_moveis_decoracao")        
    except Exception as e:
        print(f"Erro ao executar coleta: {e}")

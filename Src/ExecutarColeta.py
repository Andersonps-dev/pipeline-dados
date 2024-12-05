import subprocess
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ExecutorDeScripts:
    def __init__(self):
        self.diretorio_principal = os.path.abspath(os.getcwd())
        self.python_venv = os.path.join(self.diretorio_principal, ".venv", "Scripts", "python.exe")

    def salvar_dados_antigos(self):
        
    
    def executar_scrapy(self, coleta, nome_arquivo):
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
    executor.executar_scrapy("ofertas_games", "dados_games")
import subprocess
import os
import sys

class ExecutorDeScripts:
    def __init__(self):
        self.diretorio_principal = os.path.abspath(os.getcwd())
        self.python_venv = os.path.join(self.diretorio_principal, ".venv", "Scripts", "python.exe")
        print(self.python_venv)

    def executar_scrapy(self):
        try:
            scrapy_dir = os.path.join("pipeline-dados", "Src", "Coleta", "Coleta", "spiders")
            os.chdir(scrapy_dir)
            comando = "scrapy crawl ofertas_casa_moveis_decoracao -O ..\..\..\..\Dados\dados_casa_moveis_decoracao.jsonl"
            print(f"Executando: {comando}")
            subprocess.run(comando, shell=True, check=True)
        finally:
            os.chdir(self.diretorio_principal)

    def executar_main(self):
        main_script = os.path.join(self.diretorio_principal, "Src", "Transformacao", "main.py")
        print(f"Executando: {main_script}")
        subprocess.run([self.python_venv, main_script], check=True)

    def executar_bot(self):
        bot_script = os.path.join(self.diretorio_principal, "Src", "BotTelegram", "NotifyOfferBot.py")
        print(f"Executando: {bot_script}")
        subprocess.run([self.python_venv, bot_script], check=True)

    def executar_todos(self):
        try:
            print("Iniciando execução dos scripts...")
            self.executar_scrapy()
            self.executar_main()
            self.executar_bot()
            print("Todos os scripts foram executados com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar um dos scripts: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    executor = ExecutorDeScripts()
    executor.executar_todos()
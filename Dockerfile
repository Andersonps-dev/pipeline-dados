# Usa uma imagem base do Python
FROM python:3.11.0

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o contêiner
COPY . .

# Instrução CMD para rodar o aplicativo
CMD ["python", "Src/ControleExecucao/AgendaDisparos.py"]
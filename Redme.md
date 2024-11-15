# Sistema de Web Scraping e Integração

## 1. Coleta de Dados
- **Identificação de URLs alvo**
  - Site Mercado Livre
  - Análise da estrutura das páginas para garantir a extração correta das informações.
  - Identificação das tags da página que iremos ultilizar.

- **Implementação de rotinas de web scraping**
    - **Scrapy**: Para criar spiders que coletam dados em larga escala de forma eficiente.

## 2. Transformação de Dados
- **Estruturação de dados em Python**
  - Organizar os dados em estruturas como dicionários ou listas.

- **Conversão para formato compatível com MySQL**
  - Preparação dos dados para inserção no banco de dados, formatando como CSV ou JSON.

## 3. Armazenamento de Dados
- **Configuração do Banco de Dados MySQL**
  - Criação de um banco de dados e tabelas necessárias para armazenar os dados coletados.

- **Inserção de dados coletados no MySQL**
  - Implementação de scripts Python para inserir os dados no banco de dados.

## 4. Notificações
- **Configuração de bot no Telegram**
  - Criação de um bot no Telegram para enviar notificações.

- **Envio de alertas automáticos**
  - Implementação de triggers baseados em condições definidas (ex: novos produtos, mudanças de preço).

## 5. Containerização com Docker
- **Criação de um Dockerfile**
  - Definição do ambiente de execução, incluindo a instalação de dependências (Python, bibliotecas de scraping, MySQL connector, etc.).

- **Construção da imagem Docker**
  - Utilização do comando `docker build` para criar uma imagem que encapsula toda a aplicação.

- **Execução do container**
  - Utilização do comando `docker run` para executar a aplicação em um container isolado.

## 6. Deploy na AWS
- **Configuração de ambiente na AWS**
  - Criação de uma instância EC2 para hospedar a aplicação.

- **Criação de instâncias EC2**
  - Escolha do tipo de instância adequada para o workload do scraping.

- **Implementação de scripts de automação**
  - Configuração de scripts para inicializar automaticamente o container Docker na instância EC2.

- **Monitoramento e manutenção contínua**
  - Utilização de ferramentas como CloudWatch para monitorar a performance e a saúde da aplicação.
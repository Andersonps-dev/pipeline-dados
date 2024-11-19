# **Coleta de Dados**

## **Índice**
- [1. Identificação de URLs Alvo](#1-identificação-de-urls-alvo)
- [2. Transformação de Dados](#2-transformação-de-dados)
- [3. Armazenamento de Dados](#3-armazenamento-de-dados)
- [4. Notificações](#4-notificações)
- [5. Containerização com Docker](#5-containerização-com-docker)
- [6. Deploy na AWS](#6-deploy-na-aws)

---

## **1. Identificação de URLs Alvo**
O objetivo é coletar informações de ofertas no site **Mercado Livre**. A seguir, detalhamos o processo:

### **Estrutura e Análise das Páginas**
- Realizada uma análise da estrutura das páginas para garantir a extração precisa das informações desejadas.
- Identificadas as **tags HTML relevantes** para a coleta de dados.

### **Tags Identificadas**
As seguintes classes e atributos foram mapeados para extração das informações:.
- `poly-component__highlight`: Destaque do item na página.
- `poly-component__title`: Título ou nome do produto.
- `poly-component__price`: Informações relacionadas ao preço.
- `poly-price__current`: Preço atual do item.
- `andes-money-amount__discount`: Desconto aplicado ao produto.
- `poly-component__shipping`: Detalhes sobre o frete ou envio.

### **Tecnologia Utilizada**
- **Scrapy**: Framework para criar spiders que coletam dados de forma eficiente e escalável.

---

## **2. Transformação de Dados**
### **Estruturação em Python**
- Dados organizados em **dicionários** ou **listas**.
- Conversão para **DataFrame** usando `pandas` para facilitar o processamento.

### **Preparação para MySQL**
- Dados transformados em formatos compatíveis para inserção em banco de dados, utilizando ferramentas como `pandas.to_sql`.

---

## **3. Armazenamento de Dados**
### **Banco de Dados Postgres**
- Configuração e criação de um banco de dados(Render).
- Definição de tabelas para armazenar as informações coletadas.

### **Inserção de Dados**
- Implementação de **scripts Python** para realizar a inserção automática dos dados no banco.

---

## **4. Notificações**
### **Bot no Telegram**
- Criação e configuração de um bot no Telegram para envio de notificações automáticas.

### **Alertas Automatizados**
- Definição de **triggers** para monitorar condições específicas, como:
  - Novos produtos.
  - Alterações de preço.

---

## **5. Containerização com Docker**
### **Criação de um Dockerfile**
- Configuração do ambiente de execução, incluindo:
  - Instalação do Python.
  - Bibliotecas de scraping e conectores MySQL.

### **Construção e Execução**
- **Construção**: Criação da imagem Docker com `docker build`.
- **Execução**: Inicialização do container utilizando `docker run`.

---

## **6. Deploy na AWS**
### **Configuração de Ambiente**
- Configuração de uma instância **AWS EC2** para hospedar a aplicação.

### **Automação e Monitoramento**
- **Scripts Automáticos**: Inicialização do container Docker na instância EC2.
- **Monitoramento**: Uso do **AWS CloudWatch** para acompanhar desempenho e saúde da aplicação.

---

### 🎯 **Projeto Finalizado**
Um pipeline robusto para coleta, transformação, armazenamento e monitoramento de dados com tecnologia moderna! 🚀

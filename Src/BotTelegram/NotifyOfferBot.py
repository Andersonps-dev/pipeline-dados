import telebot
import time
from datetime import datetime
import os
import requests
import scrapy
import time
import pandas as pd
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
import schedule
import time

class NotifyOfferBot:
    def __init__(self):
        load_dotenv()
        pass
    def estancia_bot(self):
        pass
    def agendador(self):
        pass
    def envio_posts(self):
        pass


key_bot = '7674392258:AAHxopkEsTF7UEDIlof0KeGeHRFFq4yIjkQ'
id_grupo = -4547617801
bot = telebot.TeleBot(key_bot, parse_mode=None)

@bot.message_handler(commands=['teste1'])
def teste1(mensagem):
    bot.send_message(mensagem.chat.id, 'alo')
    pass

@bot.message_handler(commands=['teste2'])
def teste2(mensagem):
    bot.send_message(mensagem.chat.id, 'nada')
    pass

@bot.message_handler(commands=['teste3'])
def teste3(mensagem):
    print(mensagem)
    bot.send_message(mensagem.chat.id, 'https://www.mercadolivre.com.br/tenda-gazebo-sanfonado-articulada-dobravel-3x3m-com-mala-transporte-the-black-tools/p/MLB27293081?pdp_filters=item_id%3AMLB3583264727#polycard_client=offers&deal_print_id=eef2947f-3a22-4ec4-a5de-1e118834b595&wid=MLB3583264727&sid=offers')



def verificar(mensagem):
    return True

@bot.message_handler(commands=['help', 'ajudem', 'helpme'])
def help(message):
    texto = """
    Escolha uma opção para continuar:
    /teste1 fazer pedido
    /teste2 qualquer coisa
    /teste3 teste
    reponder qualquer coisa"""
    bot.reply_to(message, texto)



bot.infinity_polling()
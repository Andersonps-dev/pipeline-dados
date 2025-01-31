LOTE_TAMANHO = 10 # Define o tamanho do lote de mensagens que será enviadas no telegram
TEMPO_INTERVALO_LOTE = 300 # Define o tempo em segundos entre o envio de cada lote
RELEVANCIA = ["1", "2", "3"] # Relevancia definida pora os produtos


CATEGORIAS = ["dados_casa_moveis_decoracao", "dados_games"]

PALAVRAS_CHAVES = ["Jogo De", "Kit"] # Palavras que serao usadas para dar mais pontuação para itens relevantes ex: Jogo De, Kit ou cama, etc


# Comando usados que podem ser uteis -------->
    # limit_query_sql = limit_sql if limit_sql is not None else self.limit_sql
    # where_clause = " OR ".join([f"relevancia = '{relevancia}'" for relevancia in self.relevancia])
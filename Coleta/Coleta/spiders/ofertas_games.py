import scrapy


class OfertasGamesSpider(scrapy.Spider):
    name = "ofertas_games"
    start_urls = ["https://lista.mercadolivre.com.br/games"]

    def parse(self, response):
        produtos = response.css("div.poly-card__content")

        for produto in produtos:
            yield {
                'highlight': produto.css('span.andes-money-amount__fraction::text').get(),
                'titulo': produto.css('span.andes-money-amount__fraction::text').get(),
                'brand': produto.css('span.andes-money-amount__fraction::text').get(),
                'nota': produto.css('span.andes-money-amount__fraction::text').get(),
                'preco_anterior': produto.css('span.andes-money-amount__fraction::text').get(),
                'preco_atual': produto.css('span.andes-money-amount__fraction::text').get(),
                'preco_fracao': produto.css('span.andes-money-amount__fraction::text').get(),
                'porcentagem_desconto': produto.css('span.andes-money-amount__fraction::text').get(),
                'detalhe_envio': produto.css('span.andes-money-amount__fraction::text').get()
                   }

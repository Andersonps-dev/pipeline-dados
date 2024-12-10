import scrapy
from scrapy.crawler import CrawlerProcess

class OfertasCasaMoveisDecoracaoSpider(scrapy.Spider):
    name = "ofertas_casa_moveis_decoracao"
    start_urls = ["https://www.mercadolivre.com.br/ofertas?category=MLB1574"]
    
    page_count = 1
    max_pages = 10
    
    def parse(self, response):
        produtos = response.css("div.poly-card")

        for produto in produtos:

            precos = produto.css('span.andes-money-amount__fraction::text').getall()

            preco_anterior = precos[0] if len(precos) > 1 else None
            preco_atual = precos[1] if len(precos) > 1 else (precos[0] if len(precos) == 1 else None)

            yield {
                'highlight': produto.css('span.poly-component__highlight::text').get(),
                'titulo': produto.css('a.poly-component__title::text').get(), #RESERVA: 'titulo': produto.css('h2.poly-box.poly-component__title a::text').get()
                'link': produto.css('a.poly-component__title::attr(href)').get(),
                'vendido_por': produto.css('span.poly-component__seller::text').get(),
                'nota': produto.css('span.poly-reviews__rating::text').get(),
                'total_avaliacoes': produto.css('span.poly-reviews__total::text').get(),
                'preco_anterior': preco_anterior,
                'fracao_preco_anterior': produto.css('span.andes-money-amount__cents::text').get(),
                'preco_atual': preco_atual,
                'fracao_preco_atual': produto.css('span.andes-money-amount__cents.andes-money-amount__cents--superscript-24::text').get(),
                'porcentagem_desconto': produto.css('span.andes-money-amount__discount::text').get(),
                'detalhe_envio': produto.css('div.poly-component__shipping::text').get(),
                'detalhe_envio_2': produto.css('div.poly-component__shipping span::text').get(),
                'imagem': produto.css('div.poly-card__portada img::attr(data-src)').get()
                    }
            
        if self.page_count < self.max_pages:
            next_page = response.css('li.andes-pagination__button.andes-pagination__button--next a::attr(href)').get()
            if next_page:
                self.page_count += 1
                yield scrapy.Request(url=next_page, callback=self.parse)
                
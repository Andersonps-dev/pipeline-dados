import scrapy


class OfertasSpider(scrapy.Spider):
    name = "ofertas"
    allowed_domains = ["www.mercadolivre.com.br"]
    start_urls = ["https://www.mercadolivre.com.br/ofertas?category=MLB1574#filter_applied=category&filter_position=3&origin=qcat"]

    def parse(self, response):
        pass

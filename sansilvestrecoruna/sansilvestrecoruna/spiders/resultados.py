import scrapy


class ResultadosSpider(scrapy.Spider):
    name = "resultados"
    allowed_domains = ["sansilvestrecoruna.com"]
    start_urls = ["https://sansilvestrecoruna.com/es/web/resultado/"]

    def parse(self, response):
        pass

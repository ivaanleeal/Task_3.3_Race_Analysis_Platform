import scrapy
from sansilvestrecoruna.items import corredor


class ResultadosSpider(scrapy.Spider):
    name = "resultados"
    allowed_domains = ["sansilvestrecoruna.com"]
    start_urls = ["https://sansilvestrecoruna.com/es/web/resultado/competicion-16683"]

    def parse(self, response):
        """Extract book information using BookItem"""
        
        # Create a new BookItem instance
        datos = corredor()
        
        # Extract data from the page
        datos['puesto'] = response.css('td.puesto::text').get()
        datos['dorsal'] = response.css('td.dorsal::text').get()
        datos['nombre'] = response.css('td.nombre::text').get()
        datos['apellido'] = response.css('td.apellidos::text').get()
        datos['sexo'] = response.css('td.get_puesto_sexo_display::text').get()
        datos['categoría'] = response.css('td.get_puesto_categoria_display::text').get()
        datos['tiempo'] = response.css('td.tiempo_display::text').get()
        datos['carrera'] = None 
        # Extract rating (star-rating class contains the rating)
        rating_class = response.css('.star-rating::attr(class)').get()
        datos['rating'] = rating_class.replace('star-rating ', '') if rating_class else 'No rating'
        
        # Yield the item (Scrapy will process it)
        yield datos
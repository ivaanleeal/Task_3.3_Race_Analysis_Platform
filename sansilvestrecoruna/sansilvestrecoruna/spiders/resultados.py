import scrapy
from sansilvestrecoruna.items import corredor

class ResultadosSpider(scrapy.Spider):
    name = "resultados"
    allowed_domains = ["sansilvestrecoruna.com"]

    # Diccionario con el ID exacto tal cual aparece en tu lista
    MAPA_ANOS = {
        "16683": "2025",
        "15442": "2024",
        "14359": "2023",
        "13121": "2022",
        "11984": "2021",
        "10910": "2019",
        "9310":  "2018",
        "7799":  "2017",
        "6273":  "2016",
        "5000":  "2015",
        "899":   "2014",
        "-836":  "2012",
        "-603":  "2011",
        "-435":  "2010",
    }

    def start_requests(self):
        for id_comp, ano in self.MAPA_ANOS.items():
            # Construimos la URL pegando el ID
            url = f"https://sansilvestrecoruna.com/es/web/resultado/competicion-{id_comp}"
            
            # MAGIA: Le pasamos el año en el 'meta'. 
            # Así el parse() no tiene que mirar la URL ni hacer splits raros.
            yield scrapy.Request(url, callback=self.parse, meta={'ano_fijo': ano})

    def parse(self, response):
        # Recuperamos el año que guardamos en la maleta (meta)
        ano_carrera = response.meta.get('ano_fijo')

        filas = response.css('div.table-container table tbody tr')
        for fila in filas:
            datos = corredor()
            datos['puesto'] = fila.css('td.puesto::text').get()
            datos['dorsal'] = fila.css('td.dorsal a::text').get()
            datos['nombre'] = fila.css('td.nombre a::text').get()
            datos['apellido'] = fila.css('td.apellidos a::text').get()
            datos['sexo'] = fila.css('td[class*="sexo"]::text').get() 
            datos['categoría'] = fila.css('td[class*="categoria"]::text').get()
            datos['tiempo'] = fila.css('td.tiempo_display::text').get()
            
            # Usamos el año que viene en el meta
            datos['carrera'] = f"San Silvestre {ano_carrera}"
            yield datos

        # Para la paginación, volvemos a pasar el mismo año
        next_page = response.xpath('//a[contains(text(), "Siguiente")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, meta={'ano_fijo': ano_carrera})
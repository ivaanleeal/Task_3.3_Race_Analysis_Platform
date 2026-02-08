import scrapy
from sansilvestrecoruna.items import corredor

class ResultadosSpider(scrapy.Spider):
    name = "resultados"
    allowed_domains = ["sansilvestrecoruna.com"]

    MAPA_ANOS = {
        "16683": 2025,
        "15442": 2024,
        "14359": 2023,
        "13121": 2022,
        "11984": 2021,
        "10910": 2019,
        "9310":  2018,
        "7799":  2017,
        "6273":  2016,
        "5000":  2015,
        "899":   2014,
        "-836":  2012,
        "-603":  2011,
        "-435":  2010,
    }

    def start_requests(self):
        # Asignamos una prioridad base muy alta que cae drásticamente por cada año
        # Año 1: Prio 100.000, Año 2: Prio 90.000...
        prio_base = 100000
        for id_comp, ano in self.MAPA_ANOS.items():
            url = f"https://sansilvestrecoruna.com/es/web/resultado/competicion-{id_comp}"
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={'ano': ano, 'prio_actual': prio_base}, 
                priority=prio_base
            )
            prio_base -= 10000

    def parse(self, response):
        ano = response.meta['ano']
        prio_actual = response.meta['prio_actual']
        filas = response.css('div.table-container table tbody tr')

        for i, fila in enumerate(filas):
            item = corredor()
            item['puesto'] = (fila.css('td.puesto::text').get() or '').strip()
            item['dorsal'] = (fila.css('td.dorsal a::text').get() or '').strip()
            item['nombre'] = (fila.css('td.nombre a::text').get() or '').strip()
            item['apellido'] = (fila.css('td.apellidos a::text').get() or '').strip()
            item['sexo'] = (fila.css('td[class*="sexo"]::text').get() or '').strip()
            item['categoría'] = (fila.css('td[class*="categoria"]::text').get() or '').strip()
            item['tiempo'] = (fila.css('td.tiempo_display::text').get() or '').strip()
            item['carrera'] = ano
            item['ubicacion'] = 'A Coruña'

            url_perfil = fila.css('td.nombre a::attr(href)').get()

            if url_perfil:
                # Los perfiles de una página tienen prioridad sobre la página siguiente
                # Y el puesto 1 tiene prioridad sobre el puesto 2 (prio_actual + 1000 - i)
                yield response.follow(
                    url_perfil, 
                    callback=self.parse_perfil, 
                    meta={'item': item}, 
                    priority=prio_actual + 1000 - i 
                )
            else:
                item['distancia'] = "N/A"
                yield item

        # PAGINACIÓN
        next_page = response.xpath('//a[contains(text(), "Siguiente")]/@href').get()
        if next_page:
            # La página siguiente tiene menos prioridad que los perfiles actuales 
            # pero más que el año siguiente
            yield response.follow(
                next_page, 
                callback=self.parse, 
                meta={'ano': ano, 'prio_actual': prio_actual}, 
                priority=prio_actual - 1 
            )

    def parse_perfil(self, response):
        item = response.meta['item']
        distancia = response.xpath('//td[contains(text(), "KM")]/text()').get()
        if not distancia:
            distancia = response.xpath('//td[contains(text(), " m")]/text()').get()

        item['distancia'] = distancia.strip() if distancia else "N/A"
        yield item
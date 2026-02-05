import scrapy
from sansilvestrecoruna.items import corredor

class ResultadosSpider(scrapy.Spider):
    name = "resultados"
    allowed_domains = ["sansilvestrecoruna.com"]
    start_urls = ["https://sansilvestrecoruna.com/es/web/resultado/competicion-16683"]

    def parse(self, response):
        # 1. Seleccionamos TODAS las filas (tr) que están dentro del cuerpo de la tabla (tbody)
        # Basado en tu captura, las filas tienen clases "odd" o "even", pero 'tbody tr' las captura todas.
        filas = response.css('div.table-container table tbody tr')

        # 2. Iteramos sobre cada fila encontrada
        for fila in filas:
            datos = corredor()
            
            # 3. IMPORTANTE: Usamos 'fila.css' (no response.css) para buscar SOLO dentro de esa fila
            datos['puesto'] = fila.css('td.puesto::text').get()
            datos['dorsal'] = fila.css('td.dorsal a::text').get()
            datos['nombre'] = fila.css('td.nombre a::text').get()
            datos['apellido'] = fila.css('td.apellidos a::text').get()
            
            # Nota: A veces el texto está sucio (espacios), strip() ayuda a limpiarlo si get() no es None
            # datos['sexo'] = fila.css('td.get_puesto_sexo_display::text').get()
            
            datos['sexo'] = fila.css('td[class*="sexo"]::text').get() # Selector más robusto
            datos['categoría'] = fila.css('td[class*="categoria"]::text').get()
            datos['tiempo'] = fila.css('td.tiempo_display::text').get()
            datos['carrera'] = "San Silvestre Coruña"

            yield datos
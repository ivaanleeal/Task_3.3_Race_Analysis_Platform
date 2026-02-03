# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class corredor(scrapy.Item):
    """Datos del corredor"""
    puesto = scrapy.Field()
    dorsal = scrapy.Field()
    nombre = scrapy.Field()
    apellido = scrapy.Field()
    sexo = scrapy.Field()
    categoría = scrapy.Field()
    tiempo = scrapy.Field()
    carrera = scrapy.Field()

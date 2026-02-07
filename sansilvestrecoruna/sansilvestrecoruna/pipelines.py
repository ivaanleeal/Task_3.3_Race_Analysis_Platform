from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class SanSilvestreLimpiezaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 1. Limpieza de nombres y apellidos (Poner en mayúsculas y quitar espacios extra)
        for campo in ['nombre', 'apellido']:
            valor = adapter.get(campo)
            if valor:
                adapter[campo] = valor.strip().upper()

        # 2. Validación: Si el corredor no tiene nombre, lo descartamos
        if not adapter.get('nombre'):
            raise DropItem(f"Corredor sin nombre encontrado en puesto {adapter.get('puesto')}")

        return item
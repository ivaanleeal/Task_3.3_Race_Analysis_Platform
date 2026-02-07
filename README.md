# Task_3.3_Race_Analysis_Platform


## 1. Web Scraping with Scrapy


### **Valores añadidos en settings:**

**USER_AGENT**= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

- **Ignora el archivo robots.txt si prohíbe paso.**
  
	**ROBOTSTXT_OBEY**= False 

- **Especifica en que orden saldrán los datos en el CSV.**
  
	**FEED_EXPORT_FIELDS** = ['puesto', 'dorsal', 'nombre', 'apellido', 'sexo', 'categoría', 'tiempo', 'distancia', 'carrera', 'ubicacion']

- **Obliga a procesar una sola URL a la vez.**
  
	**CONCURRENT_REQUESTS** = 1

- **Un pequeño respiro para no saturar.**
  
	**DOWNLOAD_DELAY** = 0.2

- **El número 300 indica el orden de ejecución (puedes tener varios)**
  
	**ITEM_PIPELINES** = {'sansilvestrecoruna.pipelines.SanSilvestreLimpiezaPipeline': 300,}
  
---

## 2. Data Storage
## Objetivo

Guardar los datos scrapeados en JSON y cargarlos en una base de datos relacional (MariaDB).

## Requisitos

- Python 3.10+
- MariaDB 10.5+

Instalar dependencias:

```
pip install -r requirements.txt
```

## Crear MariaDB (opcion rapida con Docker)

1. Crear y levantar el contenedor:

```
docker run --name race-mariadb -e MARIADB_ROOT_PASSWORD=secret \
	-e MARIADB_DATABASE=race_results -p 3306:3306 -d mariadb:10.11
```

2. Crear las tablas:

```
docker exec -i race-mariadb mariadb -uroot -psecret race_results < sql/schema_mariadb.sql
```

## Crear MariaDB (instalacion local)

1. Instalar MariaDB Server.
2. Crear la base de datos `race_results`.
3. Ejecutar el schema:

```
mariadb -u root -p race_results < sql/schema_mariadb.sql
```

## Generar JSON desde el CSV actual

```
python scripts/export_csv_to_json.py --input sansilvestrecoruna/sansilvestrecoruna/salidas.csv --output data/salidas.json
```

## Cargar JSON a MariaDB

Configura las variables de entorno en PowerShell:

```
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="secret"
$env:DB_NAME="race_results"
```

Luego ejecuta la carga:

```
python scripts/import_json_to_mariadb.py --input data/salidas.json
```

## Entregables

- JSON con los datos: `data/salidas.json`
- Esquema SQL: `sql/schema_mariadb.sql`
- ERD: `docs/erd.md`
- Base de datos poblada con los resultados

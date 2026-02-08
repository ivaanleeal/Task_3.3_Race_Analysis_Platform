# Task 3.3 – Race Analysis Platform

## 1. Web Scraping con Scrapy

## Objetivo

Extraer información detallada de los corredores desde la web **https://sansilvestrecoruna.com/**
mediante el uso de `Scrapy`, para posteriormente generar un archivo CSV que almacene de forma estructurada los datos obtenidos durante el proceso de scraping.

## Requisitos

- **Python 3.10+**

- **Scrapy :**
  Framework de web scraping empleado para la extracción de datos desde la web.

- **Conexión a Internet :**
  Necesaria para acceder a la web https://sansilvestrecoruna.com/

Instalar dependencias:

```python
pip install -r requirements.txt
```

### Valores añadidos en `pipelines`

1. Limpieza de nombres y apellidos:
   - Conversión a mayúsculas.
   - Eliminación de espacios en blanco innecesarios.
2. Descarte de corredores sin nombre.

### Valores añadidos en `settings`

- **USER_AGENT**  
  Identifica el scraper como un navegador real (Chrome/Firefox) para evitar bloqueos por detección de bots.

```python
 USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
```

- **ROBOTSTXT_OBEY**

  Ignora las restricciones del archivo robots.txt.

```python
 ROBOTSTXT_OBEY = False
```

- **FEED_EXPORT_FIELDS**
  Define el orden de los campos en el archivo CSV generado.

```python
 FEED_EXPORT_FIELDS = [
   'puesto', 'dorsal', 'nombre', 'apellido', 'sexo',
   'categoría', 'tiempo', 'distancia', 'carrera', 'ubicacion'
]
```

- **CONCURRENT_REQUESTS**

  Fuerza el procesamiento de una sola URL simultáneamente.

```python
CONCURRENT_REQUESTS = 1
```

- **DOWNLOAD_DELAY**

  Añade un pequeño retardo entre peticiones para evitar sobrecargar el servidor.

```python
DOWNLOAD_DELAY = 0.2
```

- **ITEM_PIPELINES**

  Define el orden de ejecución del pipeline (se pueden usar varios).

```python
ITEM_PIPELINES = {
   'sansilvestrecoruna.pipelines.SanSilvestreLimpiezaPipeline': 300,
}
```

---

## 2. Data Storage

## Objetivo

Guardar los datos scrapeados en JSON y cargarlos en una base de datos relacional (MariaDB).

## Requisitos

- Python 3.10+
- MariaDB 10.5+

Instalar dependencias:

```python
pip install -r requirements.txt
```

## Crear MariaDB (opcion rapida con Docker)

1. Crear y levantar el contenedor:

```python
docker run --name race-mariadb -e MARIADB_ROOT_PASSWORD=secret \
	-e MARIADB_DATABASE=race_results -p 3306:3306 -d mariadb:10.11
```

2. Crear las tablas:

```python
docker exec -i race-mariadb mariadb -uroot -psecret race_results < sql/schema_mariadb.sql
```

## Crear MariaDB (instalacion local)

1. Instalar MariaDB Server.
2. Crear la base de datos `race_results`.
3. Ejecutar el schema:

```python
mariadb -u root -p race_results < sql/schema_mariadb.sql
```

## Generar JSON desde el CSV actual

```python
python scripts/export_csv_to_json.py --input sansilvestrecoruna/sansilvestrecoruna/salidas.csv --output data/salidas.json
```

## Cargar JSON a MariaDB

Configura las variables de entorno en PowerShell:

```python
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="secret"
$env:DB_NAME="race_results"
```

Luego ejecuta la carga:

```python
python scripts/import_json_to_mariadb.py --input data/salidas.json
```

## Entregables

- JSON con los datos: `data/salidas.json`
- Esquema SQL: `sql/schema_mariadb.sql`
- ERD: `docs/erd.md`
- Base de datos poblada con los resultados

---

## 3. Data Analytics (Analysis)

Analisis exploratorio y estadistico en notebook.

### Ejecutar el analisis

Abrir el notebook y ejecutar las celdas en orden:

- `analysis/Analysis.ipynb`

### Contenidos

- Metricas por grupo de edad y genero.
- Tendencias de participacion y tiempos (media/mediana/min/max).
- Top performers por promedio.
- Informe narrativo de hallazgos.

### Salidas

Al ejecutar el notebook se generan CSV con tablas resumen en `analysis/output/`.

---

## 4. Data Presentation (Dashboard)

Aplicacion interactiva con Streamlit para explorar carreras y corredores.

### Ejecutar la app

```python
streamlit run streamlit_app.py
```

### Funcionalidades

- Vista de carreras con filtros por genero y grupo de edad.
- Histograma de tiempos y estadisticas (min, max, media, mediana).
- Vista de corredor con historial de carreras, ritmo y posicion.
- Comparacion del corredor con la distribucion de tiempos de su carrera.

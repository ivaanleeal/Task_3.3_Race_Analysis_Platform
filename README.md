# Task_3.3_Race_Analysis_Platform

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

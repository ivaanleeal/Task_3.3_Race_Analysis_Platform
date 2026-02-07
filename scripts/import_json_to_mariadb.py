import argparse
import json
import os
from pathlib import Path

import pymysql


REQUIRED_FIELDS = ("carrera", "nombre", "apellido", "sexo", "puesto")


def parse_distance_to_meters(distance_text):
    if not distance_text:
        return None

    text = distance_text.strip().upper()
    if text.startswith("KM"):
        number = text.replace("KM", "").strip().replace(",", ".")
        try:
            return int(float(number) * 1000)
        except ValueError:
            return None

    if "M" in text:
        number = text.replace("M", "").strip().replace(",", ".")
        try:
            return int(float(number))
        except ValueError:
            return None

    return None


def parse_time_to_seconds(time_text):
    if not time_text:
        return None

    parts = time_text.strip().split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        hours = 0
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        return None

    try:
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    except ValueError:
        return None


def to_int_or_none(value):
    if value is None:
        return None

    if isinstance(value, int):
        return value

    text = str(value).strip()
    if text == "":
        return None

    try:
        return int(text)
    except ValueError:
        return None


def validate_item(item):
    missing = [field for field in REQUIRED_FIELDS if not item.get(field)]
    if missing:
        return False, f"Campos obligatorios vacios: {', '.join(missing)}"

    if to_int_or_none(item.get("carrera")) is None:
        return False, "Carrera no es un ano valido"

    if to_int_or_none(item.get("puesto")) is None:
        return False, "Puesto no es un numero valido"

    return True, ""


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "race_results"),
        charset="utf8mb4",
        autocommit=False,
    )


def upsert_race(cursor, year, location, distance_text, distance_m):
    cursor.execute(
        """
        INSERT INTO races (year, location, distance_text, distance_m)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            distance_text = VALUES(distance_text),
            distance_m = VALUES(distance_m)
        """,
        (year, location, distance_text, distance_m),
    )
    return cursor.lastrowid


def upsert_runner(cursor, first_name, last_name, sex):
    cursor.execute(
        """
        INSERT INTO runners (first_name, last_name, sex)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id)
        """,
        (first_name, last_name, sex),
    )
    return cursor.lastrowid


def upsert_result(
    cursor,
    race_id,
    runner_id,
    position,
    bib_number,
    category_code,
    time_text,
    time_seconds,
    distance_text,
    distance_m,
):
    cursor.execute(
        """
        INSERT INTO results (
            race_id,
            runner_id,
            position,
            bib_number,
            category_code,
            time_text,
            time_seconds,
            distance_text,
            distance_m
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            runner_id = VALUES(runner_id),
            bib_number = VALUES(bib_number),
            category_code = VALUES(category_code),
            time_text = VALUES(time_text),
            time_seconds = VALUES(time_seconds),
            distance_text = VALUES(distance_text),
            distance_m = VALUES(distance_m)
        """,
        (
            race_id,
            runner_id,
            position,
            bib_number,
            category_code,
            time_text,
            time_seconds,
            distance_text,
            distance_m,
        ),
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Carga resultados desde JSON a MariaDB."
    )
    parser.add_argument(
        "--input",
        default="data/salidas.json",
        help="Ruta al JSON de entrada.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Tamano de lote para commits.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {input_path}")

    with input_path.open("r", encoding="utf-8") as file_handle:
        records = json.load(file_handle)

    connection = get_connection()
    inserted = 0
    skipped = 0

    try:
        with connection.cursor() as cursor:
            for index, item in enumerate(records, start=1):
                is_valid, reason = validate_item(item)
                if not is_valid:
                    skipped += 1
                    if skipped <= 5:
                        print(f"Registro omitido ({reason}): {item}")
                    continue

                year = to_int_or_none(item.get("carrera"))
                location = item.get("ubicacion") or ""
                distance_text = item.get("distancia") or ""
                distance_m = parse_distance_to_meters(distance_text)

                race_id = upsert_race(cursor, year, location, distance_text, distance_m)

                runner_id = upsert_runner(
                    cursor,
                    item.get("nombre") or "",
                    item.get("apellido") or "",
                    item.get("sexo") or "",
                )

                position = to_int_or_none(item.get("puesto"))
                bib_number = to_int_or_none(item.get("dorsal"))
                category_code = item.get("categoria") or item.get("categoría") or ""
                time_text = item.get("tiempo") or ""
                time_seconds = parse_time_to_seconds(time_text)

                upsert_result(
                    cursor,
                    race_id,
                    runner_id,
                    position,
                    bib_number,
                    category_code,
                    time_text,
                    time_seconds,
                    distance_text,
                    distance_m,
                )

                inserted += 1

                if index % args.batch_size == 0:
                    connection.commit()

            connection.commit()

    finally:
        connection.close()

    print(f"Carga completada. Insertados: {inserted}, omitidos: {skipped}")


if __name__ == "__main__":
    main()

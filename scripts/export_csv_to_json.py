import argparse
import csv
import json
from pathlib import Path


def normalize_header(header):
    if header == "categoría":
        return "categoria"
    return header


def to_int_or_value(value):
    if value is None:
        return value
    value = value.strip()
    if value == "":
        return value
    try:
        return int(value)
    except ValueError:
        return value


def normalize_row(row):
    normalized = {}
    for key, value in row.items():
        clean_key = normalize_header(key.strip())
        clean_value = value.strip() if value is not None else ""
        normalized[clean_key] = clean_value

    for key in ("puesto", "dorsal", "carrera"):
        if key in normalized:
            normalized[key] = to_int_or_value(normalized[key])

    return normalized


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convierte el CSV de resultados a JSON para respaldo."
    )
    parser.add_argument(
        "--input",
        default="sansilvestrecoruna/sansilvestrecoruna/salidas.csv",
        help="Ruta al CSV de entrada.",
    )
    parser.add_argument(
        "--output",
        default="data/salidas.json",
        help="Ruta al JSON de salida.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        records = [normalize_row(row) for row in reader]

    with output_path.open("w", encoding="utf-8") as file_handle:
        json.dump(records, file_handle, ensure_ascii=False, indent=2)

    print(f"JSON generado: {output_path} ({len(records)} registros)")


if __name__ == "__main__":
    main()

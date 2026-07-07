from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import psycopg
from psycopg import sql


def table_name_from_file(path: Path) -> str:
    return path.stem.lower()


def read_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-16-le", newline="") as file:
        reader = csv.reader(file)
        return next(reader)


def recreate_legacy_table(conn: psycopg.Connection, table_name: str, columns: list[str]) -> None:
    column_defs = [
        sql.SQL("{} text").format(sql.Identifier(column))
        for column in columns
    ]
    create_statement = sql.SQL("CREATE TABLE legacy.{} ({})").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(column_defs),
    )

    with conn.cursor() as cur:
        cur.execute(sql.SQL("DROP TABLE IF EXISTS legacy.{}").format(sql.Identifier(table_name)))
        cur.execute(create_statement)


def import_file(conn: psycopg.Connection, path: Path) -> int:
    table_name = table_name_from_file(path)
    columns = read_header(path)
    recreate_legacy_table(conn, table_name, columns)

    with path.open("r", encoding="utf-16-le", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        rows = list(reader)

    if not rows:
        return 0

    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
    insert_statement = sql.SQL("INSERT INTO legacy.{} ({}) VALUES ({})").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        placeholders,
    )

    with conn.cursor() as cur:
        cur.executemany(insert_statement, rows)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa CSVs HFSQL para o schema legacy.")
    parser.add_argument("--input", default="../ExportHFSQL", help="Diretorio com CSVs exportados.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("LEGACY_DATABASE_URL", "postgresql://eletron:eletron_dev@127.0.0.1:5432/eletron"),
        help="URL psycopg do PostgreSQL.",
    )
    parser.add_argument("--only", nargs="*", help="Lista opcional de arquivos/stems para importar.")
    args = parser.parse_args()

    input_dir = Path(args.input)
    selected = {item.lower().removesuffix(".csv") for item in args.only or []}
    csv_files = sorted(input_dir.glob("*.csv"))
    if selected:
        csv_files = [path for path in csv_files if path.stem.lower() in selected]

    with psycopg.connect(args.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS legacy")

        for path in csv_files:
            count = import_file(conn, path)
            print(f"{path.name}: {count} registros")

    print("Importacao legacy concluida.")


if __name__ == "__main__":
    main()

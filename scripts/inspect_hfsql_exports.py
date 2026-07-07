from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def inspect_file(path: Path) -> dict:
    with path.open("r", encoding="utf-16-le", newline="") as file:
        reader = csv.reader(file)
        try:
            header = next(reader)
        except StopIteration:
            return {
                "file": path.name,
                "columns": [],
                "column_count": 0,
                "row_count": 0,
                "size_bytes": path.stat().st_size,
            }

        row_count = sum(1 for _ in reader)

    return {
        "file": path.name,
        "columns": header,
        "column_count": len(header),
        "row_count": row_count,
        "size_bytes": path.stat().st_size,
    }


def write_markdown(inventory: list[dict], output_path: Path) -> None:
    lines = [
        "# Inventario dos exports HFSQL",
        "",
        "| Arquivo | Registros | Colunas | Tamanho KB |",
        "| --- | ---: | ---: | ---: |",
    ]

    for item in sorted(inventory, key=lambda row: row["row_count"], reverse=True):
        size_kb = item["size_bytes"] / 1024
        lines.append(
            f"| `{item['file']}` | {item['row_count']} | {item['column_count']} | {size_kb:.1f} |"
        )

    lines.extend(["", "## Colunas", ""])

    for item in sorted(inventory, key=lambda row: row["file"].lower()):
        lines.append(f"### `{item['file']}`")
        lines.append("")
        for column in item["columns"]:
            lines.append(f"- `{column}`")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspeciona CSVs exportados do HFSQL.")
    parser.add_argument("--input", default="ExportHFSQL", help="Diretorio com CSVs.")
    parser.add_argument("--json", default="docs/inventario-hfsql.json", help="Arquivo JSON de saida.")
    parser.add_argument("--md", default="docs/inventario-hfsql.md", help="Arquivo Markdown de saida.")
    args = parser.parse_args()

    input_dir = Path(args.input)
    inventory = [inspect_file(path) for path in sorted(input_dir.glob("*.csv"))]

    json_path = Path(args.json)
    md_path = Path(args.md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(inventory, md_path)

    print(f"Arquivos analisados: {len(inventory)}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import os

import psycopg

from app.core.security import get_password_hash


def main() -> None:
    parser = argparse.ArgumentParser(description="Define uma nova senha para um usuario local.")
    parser.add_argument("login", help="Username, nome, email ou codigo Proton.")
    parser.add_argument("senha", help="Nova senha.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("LEGACY_DATABASE_URL", "postgresql://eletron:eletron_dev@127.0.0.1:5433/eletron"),
    )
    args = parser.parse_args()

    login = args.login.strip()
    login_lower = login.lower()
    senha_hash = get_password_hash(args.senha)

    with psycopg.connect(args.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE usuarios
                SET senha_hash = %s,
                    senha_deve_alterar = false
                WHERE username = %s
                   OR lower(nome) = %s
                   OR lower(coalesce(email, '')) = %s
                   OR cod_proton::text = %s
                RETURNING id, nome, username
                """,
                (senha_hash, login_lower, login_lower, login_lower, login),
            )
            row = cur.fetchone()

    if row is None:
        raise SystemExit(f"Usuario nao encontrado: {login}")

    print(f"Senha atualizada: id={row[0]} nome={row[1]} username={row[2]}")


if __name__ == "__main__":
    main()

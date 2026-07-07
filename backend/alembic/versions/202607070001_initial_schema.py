"""initial schema

Revision ID: 202607070001
Revises:
Create Date: 2026-07-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "202607070001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS legacy")

    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_empresa_id", sa.Integer(), nullable=True),
        sa.Column("proton_id", sa.Integer(), nullable=True),
        sa.Column("fantasia", sa.String(length=120), nullable=False),
        sa.Column("cnpj", sa.String(length=20), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_empresas_legacy_empresa_id", "empresas", ["legacy_empresa_id"], unique=True)
    op.create_index("ix_empresas_proton_id", "empresas", ["proton_id"])
    op.create_index("ix_empresas_cnpj", "empresas", ["cnpj"])

    op.create_table(
        "formas_pagamento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_forma_pagamento_id", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=True),
        sa.Column("percentual_desconto", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_formas_pagamento_legacy_forma_pagamento_id",
        "formas_pagamento",
        ["legacy_forma_pagamento_id"],
        unique=True,
    )

    op.create_table(
        "reservas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_reserva_id", sa.Integer(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.Date(), nullable=True),
        sa.Column("hora", sa.Time(), nullable=True),
        sa.Column("vendedor_id", sa.Integer(), nullable=True),
        sa.Column("vendedor_nome", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=True),
        sa.Column("forma_pagamento_id", sa.Integer(), nullable=True),
        sa.Column("valor_total", sa.Numeric(14, 2), nullable=True),
        sa.Column("valor_desconto", sa.Numeric(14, 2), nullable=True),
        sa.Column("valor_liquido", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_pago", sa.Numeric(14, 2), nullable=True),
        sa.Column("troco", sa.Numeric(14, 2), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reservas_legacy_reserva_id", "reservas", ["legacy_reserva_id"], unique=True)
    op.create_index("ix_reservas_empresa_id", "reservas", ["empresa_id"])
    op.create_index("ix_reservas_vendedor_id", "reservas", ["vendedor_id"])
    op.create_index("ix_reservas_status", "reservas", ["status"])

    op.create_table(
        "reserva_itens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_item_id", sa.Integer(), nullable=True),
        sa.Column("reserva_id", sa.Integer(), nullable=False),
        sa.Column("produto_codigo", sa.String(length=60), nullable=True),
        sa.Column("produto_nome", sa.String(length=255), nullable=True),
        sa.Column("valor_unitario", sa.Numeric(14, 2), nullable=True),
        sa.Column("quantidade", sa.Numeric(14, 4), nullable=True),
        sa.Column("valor_total", sa.Numeric(14, 2), nullable=True),
        sa.Column("percentual_desconto", sa.Numeric(8, 4), nullable=True),
        sa.Column("valor_desconto", sa.Numeric(14, 2), nullable=True),
        sa.Column("valor_final", sa.Numeric(14, 2), nullable=True),
        sa.Column("grupo_codigo", sa.String(length=60), nullable=True),
        sa.Column("grupo_descricao", sa.String(length=120), nullable=True),
        sa.Column("tamanho", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["reserva_id"], ["reservas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reserva_itens_legacy_item_id", "reserva_itens", ["legacy_item_id"], unique=True)
    op.create_index("ix_reserva_itens_reserva_id", "reserva_itens", ["reserva_id"])
    op.create_index("ix_reserva_itens_produto_codigo", "reserva_itens", ["produto_codigo"])

    op.create_table(
        "legacy_table_map",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_table", sa.String(length=120), nullable=False),
        sa.Column("target_table", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("legacy_table_map")
    op.drop_index("ix_reserva_itens_produto_codigo", table_name="reserva_itens")
    op.drop_index("ix_reserva_itens_reserva_id", table_name="reserva_itens")
    op.drop_index("ix_reserva_itens_legacy_item_id", table_name="reserva_itens")
    op.drop_table("reserva_itens")
    op.drop_index("ix_reservas_status", table_name="reservas")
    op.drop_index("ix_reservas_vendedor_id", table_name="reservas")
    op.drop_index("ix_reservas_empresa_id", table_name="reservas")
    op.drop_index("ix_reservas_legacy_reserva_id", table_name="reservas")
    op.drop_table("reservas")
    op.drop_index("ix_formas_pagamento_legacy_forma_pagamento_id", table_name="formas_pagamento")
    op.drop_table("formas_pagamento")
    op.drop_index("ix_empresas_cnpj", table_name="empresas")
    op.drop_index("ix_empresas_proton_id", table_name="empresas")
    op.drop_index("ix_empresas_legacy_empresa_id", table_name="empresas")
    op.drop_table("empresas")
    op.execute("DROP SCHEMA IF EXISTS legacy CASCADE")

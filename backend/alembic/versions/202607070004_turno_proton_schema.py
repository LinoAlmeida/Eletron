"""turno and proton schema

Revision ID: 202607070004
Revises: 202607070003
Create Date: 2026-07-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "202607070004"
down_revision: Union[str, None] = "202607070003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vendedores_filiais",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_vendedor_filial_id", sa.Integer(), nullable=True),
        sa.Column("vendedor_proton_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=True),
        sa.Column("nome_abreviado", sa.String(length=80), nullable=True),
        sa.Column("cpf_cnpj", sa.String(length=20), nullable=True),
        sa.Column("filial_proton_id", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vendedor_proton_id", "filial_proton_id", name="uq_vendedores_filiais_vend_filial"),
    )
    op.create_index("ix_vendedores_filiais_legacy_vendedor_filial_id", "vendedores_filiais", ["legacy_vendedor_filial_id"], unique=True)
    op.create_index("ix_vendedores_filiais_vendedor_proton_id", "vendedores_filiais", ["vendedor_proton_id"])
    op.create_index("ix_vendedores_filiais_cpf_cnpj", "vendedores_filiais", ["cpf_cnpj"])
    op.create_index("ix_vendedores_filiais_filial_proton_id", "vendedores_filiais", ["filial_proton_id"])


def downgrade() -> None:
    op.drop_index("ix_vendedores_filiais_filial_proton_id", table_name="vendedores_filiais")
    op.drop_index("ix_vendedores_filiais_cpf_cnpj", table_name="vendedores_filiais")
    op.drop_index("ix_vendedores_filiais_vendedor_proton_id", table_name="vendedores_filiais")
    op.drop_index("ix_vendedores_filiais_legacy_vendedor_filial_id", table_name="vendedores_filiais")
    op.drop_table("vendedores_filiais")

"""financeiro schema

Revision ID: 202607070003
Revises: 202607070002
Create Date: 2026-07-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "202607070003"
down_revision: Union[str, None] = "202607070002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "caixas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_caixa_id", sa.Integer(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("filial_proton", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("usuario_nome", sa.String(length=120), nullable=True),
        sa.Column("cod_proton_usuario", sa.Integer(), nullable=True),
        sa.Column("data_abertura", sa.Date(), nullable=True),
        sa.Column("hora_abertura", sa.Time(), nullable=True),
        sa.Column("data_fechamento", sa.Date(), nullable=True),
        sa.Column("hora_fechamento", sa.Time(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=True),
        sa.Column("valor_inicial", sa.Numeric(14, 2), nullable=True),
        sa.Column("valor_final", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_dinheiro", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_pix", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_credito", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_debito", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_sangria", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_link", sa.Numeric(14, 2), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_caixas_legacy_caixa_id", "caixas", ["legacy_caixa_id"], unique=True)
    op.create_index("ix_caixas_empresa_id", "caixas", ["empresa_id"])
    op.create_index("ix_caixas_filial_proton", "caixas", ["filial_proton"])
    op.create_index("ix_caixas_usuario_id", "caixas", ["usuario_id"])
    op.create_index("ix_caixas_cod_proton_usuario", "caixas", ["cod_proton_usuario"])
    op.create_index("ix_caixas_status", "caixas", ["status"])

    op.create_table(
        "titulos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_titulo_id", sa.Integer(), nullable=True),
        sa.Column("caixa_id", sa.Integer(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("reserva_id", sa.Integer(), nullable=True),
        sa.Column("forma_pagamento_id", sa.Integer(), nullable=True),
        sa.Column("valor", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=True),
        sa.Column("data", sa.Date(), nullable=True),
        sa.Column("hora", sa.Time(), nullable=True),
        sa.Column("data_cancelamento", sa.Date(), nullable=True),
        sa.Column("hora_cancelamento", sa.Time(), nullable=True),
        sa.Column("data_aprovacao", sa.Date(), nullable=True),
        sa.Column("hora_aprovacao", sa.Time(), nullable=True),
        sa.Column("qrcode_id", sa.String(length=120), nullable=True),
        sa.Column("qrcode", sa.Text(), nullable=True),
        sa.Column("order_pay", sa.String(length=120), nullable=True),
        sa.Column("asaas_id", sa.String(length=120), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("tipo_live", sa.String(length=40), nullable=True),
        sa.Column("cod_autorizacao", sa.String(length=80), nullable=True),
        sa.Column("cod_autorizacao_pix", sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["caixa_id"], ["caixas.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["forma_pagamento_id"], ["formas_pagamento.id"]),
        sa.ForeignKeyConstraint(["reserva_id"], ["reservas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_titulos_legacy_titulo_id", "titulos", ["legacy_titulo_id"], unique=True)
    op.create_index("ix_titulos_caixa_id", "titulos", ["caixa_id"])
    op.create_index("ix_titulos_empresa_id", "titulos", ["empresa_id"])
    op.create_index("ix_titulos_reserva_id", "titulos", ["reserva_id"])
    op.create_index("ix_titulos_forma_pagamento_id", "titulos", ["forma_pagamento_id"])
    op.create_index("ix_titulos_status", "titulos", ["status"])


def downgrade() -> None:
    op.drop_index("ix_titulos_status", table_name="titulos")
    op.drop_index("ix_titulos_forma_pagamento_id", table_name="titulos")
    op.drop_index("ix_titulos_reserva_id", table_name="titulos")
    op.drop_index("ix_titulos_empresa_id", table_name="titulos")
    op.drop_index("ix_titulos_caixa_id", table_name="titulos")
    op.drop_index("ix_titulos_legacy_titulo_id", table_name="titulos")
    op.drop_table("titulos")
    op.drop_index("ix_caixas_status", table_name="caixas")
    op.drop_index("ix_caixas_cod_proton_usuario", table_name="caixas")
    op.drop_index("ix_caixas_usuario_id", table_name="caixas")
    op.drop_index("ix_caixas_filial_proton", table_name="caixas")
    op.drop_index("ix_caixas_empresa_id", table_name="caixas")
    op.drop_index("ix_caixas_legacy_caixa_id", table_name="caixas")
    op.drop_table("caixas")

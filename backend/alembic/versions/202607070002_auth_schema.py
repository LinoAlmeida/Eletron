"""auth schema

Revision ID: 202607070002
Revises: 202607070001
Create Date: 2026-07-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "202607070002"
down_revision: Union[str, None] = "202607070001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "perfis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_nivel_id", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_index("ix_perfis_legacy_nivel_id", "perfis", ["legacy_nivel_id"], unique=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_usuario_id", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=160), nullable=True),
        sa.Column("cpf", sa.String(length=20), nullable=True),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("cod_proton", sa.Integer(), nullable=True),
        sa.Column("perfil_id", sa.Integer(), nullable=True),
        sa.Column("filial", sa.Integer(), nullable=True),
        sa.Column("empresa_padrao_id", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("senha_deve_alterar", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["perfil_id"], ["perfis.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_legacy_usuario_id", "usuarios", ["legacy_usuario_id"], unique=True)
    op.create_index("ix_usuarios_nome", "usuarios", ["nome"])
    op.create_index("ix_usuarios_username", "usuarios", ["username"], unique=True)
    op.create_index("ix_usuarios_email", "usuarios", ["email"])
    op.create_index("ix_usuarios_cpf", "usuarios", ["cpf"])
    op.create_index("ix_usuarios_cod_proton", "usuarios", ["cod_proton"])
    op.create_index("ix_usuarios_perfil_id", "usuarios", ["perfil_id"])
    op.create_index("ix_usuarios_empresa_padrao_id", "usuarios", ["empresa_padrao_id"])

    op.create_table(
        "usuarios_empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legacy_usuario_empresa_id", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "empresa_id", name="uq_usuarios_empresas_usuario_empresa"),
    )
    op.create_index(
        "ix_usuarios_empresas_legacy_usuario_empresa_id",
        "usuarios_empresas",
        ["legacy_usuario_empresa_id"],
        unique=True,
    )
    op.create_index("ix_usuarios_empresas_usuario_id", "usuarios_empresas", ["usuario_id"])
    op.create_index("ix_usuarios_empresas_empresa_id", "usuarios_empresas", ["empresa_id"])


def downgrade() -> None:
    op.drop_index("ix_usuarios_empresas_empresa_id", table_name="usuarios_empresas")
    op.drop_index("ix_usuarios_empresas_usuario_id", table_name="usuarios_empresas")
    op.drop_index("ix_usuarios_empresas_legacy_usuario_empresa_id", table_name="usuarios_empresas")
    op.drop_table("usuarios_empresas")
    op.drop_index("ix_usuarios_empresa_padrao_id", table_name="usuarios")
    op.drop_index("ix_usuarios_perfil_id", table_name="usuarios")
    op.drop_index("ix_usuarios_cod_proton", table_name="usuarios")
    op.drop_index("ix_usuarios_cpf", table_name="usuarios")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_index("ix_usuarios_username", table_name="usuarios")
    op.drop_index("ix_usuarios_nome", table_name="usuarios")
    op.drop_index("ix_usuarios_legacy_usuario_id", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_index("ix_perfis_legacy_nivel_id", table_name="perfis")
    op.drop_table("perfis")

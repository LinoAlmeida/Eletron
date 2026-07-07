from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VendedorFilial(Base):
    __tablename__ = "vendedores_filiais"
    __table_args__ = (
        UniqueConstraint("vendedor_proton_id", "filial_proton_id", name="uq_vendedores_filiais_vend_filial"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_vendedor_filial_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    vendedor_proton_id: Mapped[int] = mapped_column(Integer, index=True)
    nome: Mapped[str | None] = mapped_column(String(120))
    nome_abreviado: Mapped[str | None] = mapped_column(String(80))
    cpf_cnpj: Mapped[str | None] = mapped_column(String(20), index=True)
    filial_proton_id: Mapped[int] = mapped_column(Integer, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

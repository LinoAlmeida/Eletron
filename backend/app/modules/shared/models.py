from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_empresa_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    proton_id: Mapped[int | None] = mapped_column(Integer, index=True)
    fantasia: Mapped[str] = mapped_column(String(120))
    cnpj: Mapped[str | None] = mapped_column(String(20), index=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)


class FormaPagamento(Base):
    __tablename__ = "formas_pagamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_forma_pagamento_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str | None] = mapped_column(String(40))
    percentual_desconto: Mapped[str | None] = mapped_column(String(30))

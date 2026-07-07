from datetime import date, time
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Caixa(Base):
    __tablename__ = "caixas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_caixa_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id"), index=True)
    filial_proton: Mapped[int | None] = mapped_column(Integer, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), index=True)
    usuario_nome: Mapped[str | None] = mapped_column(String(120))
    cod_proton_usuario: Mapped[int | None] = mapped_column(Integer, index=True)
    data_abertura: Mapped[date | None] = mapped_column(Date)
    hora_abertura: Mapped[time | None] = mapped_column(Time)
    data_fechamento: Mapped[date | None] = mapped_column(Date)
    hora_fechamento: Mapped[time | None] = mapped_column(Time)
    status: Mapped[str | None] = mapped_column(String(40), index=True)
    valor_inicial: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valor_final: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_dinheiro: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_pix: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_credito: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_debito: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_sangria: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_link: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))

    titulos: Mapped[list["Titulo"]] = relationship(back_populates="caixa")


class Titulo(Base):
    __tablename__ = "titulos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_titulo_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    caixa_id: Mapped[int | None] = mapped_column(ForeignKey("caixas.id"), index=True)
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id"), index=True)
    reserva_id: Mapped[int | None] = mapped_column(ForeignKey("reservas.id"), index=True)
    forma_pagamento_id: Mapped[int | None] = mapped_column(ForeignKey("formas_pagamento.id"), index=True)
    valor: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    status: Mapped[str | None] = mapped_column(String(40), index=True)
    data: Mapped[date | None] = mapped_column(Date)
    hora: Mapped[time | None] = mapped_column(Time)
    data_cancelamento: Mapped[date | None] = mapped_column(Date)
    hora_cancelamento: Mapped[time | None] = mapped_column(Time)
    data_aprovacao: Mapped[date | None] = mapped_column(Date)
    hora_aprovacao: Mapped[time | None] = mapped_column(Time)
    qrcode_id: Mapped[str | None] = mapped_column(String(120))
    qrcode: Mapped[str | None] = mapped_column(Text)
    order_pay: Mapped[str | None] = mapped_column(String(120))
    asaas_id: Mapped[str | None] = mapped_column(String(120))
    url: Mapped[str | None] = mapped_column(Text)
    tipo_live: Mapped[str | None] = mapped_column(String(40))
    cod_autorizacao: Mapped[str | None] = mapped_column(String(80))
    cod_autorizacao_pix: Mapped[str | None] = mapped_column(String(80))

    caixa: Mapped[Caixa | None] = relationship(back_populates="titulos")

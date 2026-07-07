from datetime import date, time
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reserva(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_reserva_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    empresa_id: Mapped[int | None] = mapped_column(Integer, index=True)
    data: Mapped[date | None] = mapped_column(Date)
    hora: Mapped[time | None] = mapped_column(Time)
    vendedor_id: Mapped[int | None] = mapped_column(Integer, index=True)
    vendedor_nome: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str | None] = mapped_column(String(40), index=True)
    forma_pagamento_id: Mapped[int | None] = mapped_column(Integer)
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valor_desconto: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valor_liquido: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_pago: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    troco: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    observacao: Mapped[str | None] = mapped_column(Text)

    itens: Mapped[list["ReservaItem"]] = relationship(back_populates="reserva")


class ReservaItem(Base):
    __tablename__ = "reserva_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_item_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.id"), index=True)
    produto_codigo: Mapped[str | None] = mapped_column(String(60), index=True)
    produto_nome: Mapped[str | None] = mapped_column(String(255))
    valor_unitario: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    percentual_desconto: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    valor_desconto: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valor_final: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    grupo_codigo: Mapped[str | None] = mapped_column(String(60))
    grupo_descricao: Mapped[str | None] = mapped_column(String(120))
    tamanho: Mapped[str | None] = mapped_column(String(40))

    reserva: Mapped[Reserva] = relationship(back_populates="itens")

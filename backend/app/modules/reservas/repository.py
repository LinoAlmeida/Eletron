from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.financeiro.models import Caixa, Titulo
from app.modules.reservas.models import Reserva, ReservaItem


class ReservaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, *, limit: int, offset: int, empresa_id: int | None) -> list[Reserva]:
        statement: Select[tuple[Reserva]] = (
            select(Reserva).order_by(Reserva.data.desc().nullslast(), Reserva.id.desc()).limit(limit).offset(offset)
        )
        if empresa_id is not None:
            statement = statement.where(Reserva.empresa_id == empresa_id)
        return list(self.db.scalars(statement))

    def count(self, *, empresa_id: int | None) -> int:
        statement = select(func.count()).select_from(Reserva)
        if empresa_id is not None:
            statement = statement.where(Reserva.empresa_id == empresa_id)
        return int(self.db.scalar(statement) or 0)

    def get(self, *, reserva_id: int, empresa_id: int | None) -> Reserva | None:
        statement = select(Reserva).where(Reserva.id == reserva_id)
        if empresa_id is not None:
            statement = statement.where(Reserva.empresa_id == empresa_id)
        return self.db.scalar(statement)

    def list_itens(self, *, reserva_id: int) -> list[ReservaItem]:
        statement = select(ReservaItem).where(ReservaItem.reserva_id == reserva_id).order_by(ReservaItem.id)
        return list(self.db.scalars(statement))

    def list_titulos(self, *, reserva_id: int, empresa_id: int | None) -> list[Titulo]:
        statement = select(Titulo).where(Titulo.reserva_id == reserva_id).order_by(Titulo.id)
        if empresa_id is not None:
            statement = statement.where(Titulo.empresa_id == empresa_id)
        return list(self.db.scalars(statement))

    def list_caixas_by_titulos(self, *, caixa_ids: set[int]) -> list[Caixa]:
        if not caixa_ids:
            return []
        statement = select(Caixa).where(Caixa.id.in_(caixa_ids)).order_by(Caixa.id)
        return list(self.db.scalars(statement))

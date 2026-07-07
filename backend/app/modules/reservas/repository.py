from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.reservas.models import Reserva


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

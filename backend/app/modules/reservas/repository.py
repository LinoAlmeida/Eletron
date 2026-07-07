from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.reservas.models import Reserva


class ReservaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, *, limit: int, offset: int) -> list[Reserva]:
        statement: Select[tuple[Reserva]] = (
            select(Reserva).order_by(Reserva.data.desc().nullslast(), Reserva.id.desc()).limit(limit).offset(offset)
        )
        return list(self.db.scalars(statement))

    def count(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(Reserva)) or 0)

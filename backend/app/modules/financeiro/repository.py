from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.financeiro.models import Caixa, Titulo


class FinanceiroRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_titulos_by_reserva(self, *, reserva_id: int, empresa_id: int | None) -> list[Titulo]:
        statement = select(Titulo).where(Titulo.reserva_id == reserva_id).order_by(Titulo.id)
        if empresa_id is not None:
            statement = statement.where(Titulo.empresa_id == empresa_id)
        return list(self.db.scalars(statement))

    def count_titulos_by_reserva(self, *, reserva_id: int, empresa_id: int | None) -> int:
        statement = select(func.count()).select_from(Titulo).where(Titulo.reserva_id == reserva_id)
        if empresa_id is not None:
            statement = statement.where(Titulo.empresa_id == empresa_id)
        return int(self.db.scalar(statement) or 0)

    def list_caixas(self, *, empresa_id: int | None, limit: int, offset: int) -> list[Caixa]:
        statement = select(Caixa).order_by(Caixa.data_abertura.desc().nullslast(), Caixa.id.desc())
        if empresa_id is not None:
            statement = statement.where(Caixa.empresa_id == empresa_id)
        return list(self.db.scalars(statement.limit(limit).offset(offset)))

    def count_caixas(self, *, empresa_id: int | None) -> int:
        statement = select(func.count()).select_from(Caixa)
        if empresa_id is not None:
            statement = statement.where(Caixa.empresa_id == empresa_id)
        return int(self.db.scalar(statement) or 0)

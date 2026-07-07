from sqlalchemy.orm import Session

from app.modules.reservas.repository import ReservaRepository
from app.modules.reservas.schemas import ReservaListResponse


class ReservaService:
    def __init__(self, db: Session) -> None:
        self.repository = ReservaRepository(db)

    def listar(self, *, limit: int, offset: int) -> ReservaListResponse:
        return ReservaListResponse(
            total=self.repository.count(),
            items=self.repository.list(limit=limit, offset=offset),
        )

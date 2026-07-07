from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.auth.models import Usuario, UsuarioEmpresa
from app.modules.shared.models import Empresa


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_usuario_by_id(self, usuario_id: int) -> Usuario | None:
        statement = (
            select(Usuario)
            .options(selectinload(Usuario.perfil))
            .where(Usuario.id == usuario_id, Usuario.ativo.is_(True))
        )
        return self.db.scalar(statement)

    def get_usuario_by_login(self, login: str) -> Usuario | None:
        login_clean = login.strip()
        login_lower = login_clean.lower()
        cod_proton = int(login_clean) if login_clean.isdigit() else None

        filters = [
            Usuario.username == login_lower,
            Usuario.email == login_lower,
            Usuario.cpf == login_clean,
            Usuario.nome.ilike(login_clean),
        ]
        if cod_proton is not None:
            filters.append(Usuario.cod_proton == cod_proton)

        statement = (
            select(Usuario)
            .options(selectinload(Usuario.perfil))
            .where(Usuario.ativo.is_(True), or_(*filters))
            .limit(1)
        )
        return self.db.scalar(statement)

    def list_empresas_usuario(self, usuario_id: int) -> list[Empresa]:
        statement = (
            select(Empresa)
            .join(UsuarioEmpresa, UsuarioEmpresa.empresa_id == Empresa.id)
            .where(UsuarioEmpresa.usuario_id == usuario_id, Empresa.ativa.is_(True))
            .order_by(Empresa.fantasia)
        )
        return list(self.db.scalars(statement))

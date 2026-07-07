from sqlalchemy import select
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

    def get_usuario_by_cod_proton(self, cod_proton: int) -> Usuario | None:
        statement = (
            select(Usuario)
            .options(selectinload(Usuario.perfil))
            .where(Usuario.ativo.is_(True), Usuario.cod_proton == cod_proton)
            .limit(1)
        )
        return self.db.scalar(statement)

    def get_usuario_by_login(self, login: str) -> Usuario | None:
        login_clean = login.strip()
        if not login_clean.isdigit():
            return None
        cod_proton = int(login_clean)
        statement = (
            select(Usuario)
            .options(selectinload(Usuario.perfil))
            .where(Usuario.ativo.is_(True), Usuario.cod_proton == cod_proton)
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

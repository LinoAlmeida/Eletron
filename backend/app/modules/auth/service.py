from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import ALGORITHM, create_access_token, verify_password
from app.modules.auth.models import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse
from app.modules.proton.service import ProtonService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuthRepository(db)

    def login(self, login: str, senha: str) -> TokenResponse:
        if not login.strip().isdigit():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Informe o codigo Proton do operador.",
            )

        usuario = self.repository.get_usuario_by_login(login)
        if usuario is None or not verify_password(senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha invalidos.",
            )

        token = create_access_token(
            subject=str(usuario.id),
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

        sincronizados = 0
        try:
            sincronizados = ProtonService(self.db).sincronizar_vendedores_filiais()
            self.db.commit()
        except Exception:
            self.db.rollback()

        return TokenResponse(
            access_token=token,
            usuario={
                "id": usuario.id,
                "legacy_usuario_id": usuario.legacy_usuario_id,
                "nome": usuario.nome,
                "username": usuario.username,
                "email": usuario.email,
                "cod_proton": usuario.cod_proton,
                "perfil": usuario.perfil,
                "empresa_padrao_id": usuario.empresa_padrao_id,
                "senha_deve_alterar": usuario.senha_deve_alterar,
                "glo_id_user": usuario.id,
                "glo_tp_user": usuario.perfil_id,
                "glo_empresa": usuario.empresa_padrao_id,
                "glo_id_proton": usuario.cod_proton,
            },
            vendedores_filiais_sincronizados=sincronizados,
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        usuario_id = int(subject)
    except (JWTError, ValueError) as exc:
        raise credentials_exception from exc

    usuario = AuthRepository(db).get_usuario_by_id(usuario_id)
    if usuario is None:
        raise credentials_exception
    return usuario

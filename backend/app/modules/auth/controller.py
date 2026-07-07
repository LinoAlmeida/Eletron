from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import EmpresaAuthOut, LoginRequest, TokenResponse, UsuarioOut
from app.modules.auth.service import AuthService, get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService(db).login(payload.login, payload.senha)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario


@router.get("/empresas", response_model=list[EmpresaAuthOut])
def minhas_empresas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> list[EmpresaAuthOut]:
    empresas = AuthRepository(db).list_empresas_usuario(usuario.id)
    return [EmpresaAuthOut(id=empresa.id, fantasia=empresa.fantasia, cnpj=empresa.cnpj) for empresa in empresas]

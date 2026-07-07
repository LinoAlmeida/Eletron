from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.models import Usuario
from app.modules.auth.service import get_current_user
from app.modules.pdv.schemas import EstoqueOut, ProdutoBuscaOut, VendedorOut
from app.modules.pdv.service import PdvService

router = APIRouter()


@router.get("/estoques", response_model=list[EstoqueOut])
def listar_estoques(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> list[EstoqueOut]:
    return PdvService(db).listar_estoques(usuario)


@router.get("/vendedores", response_model=list[VendedorOut])
def listar_vendedores(
    filial_proton_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> list[VendedorOut]:
    return PdvService(db).listar_vendedores(filial_proton_id)


@router.get("/produtos/buscar", response_model=ProdutoBuscaOut)
def buscar_produto(
    cod_fil: int = Query(..., ge=1),
    codprod: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> ProdutoBuscaOut:
    return PdvService(db).buscar_produto(cod_fil=cod_fil, codprod=codprod)

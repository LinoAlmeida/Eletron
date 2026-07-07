from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.pdv.repository import PdvRepository
from app.modules.pdv.schemas import EstoqueOut, ProdutoBuscaOut, VendedorOut
from app.modules.proton.service import ProtonService


class PdvService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PdvRepository(db)

    def listar_estoques(self, usuario: Usuario) -> list[EstoqueOut]:
        empresas = self.repository.list_estoques_usuario(usuario.id)
        return [EstoqueOut.model_validate(empresa) for empresa in empresas]

    def listar_vendedores(self, filial_proton_id: int) -> list[VendedorOut]:
        vendedores = self.repository.list_vendedores_filial(filial_proton_id)
        return [VendedorOut.model_validate(vendedor) for vendedor in vendedores]

    def buscar_produto(self, *, cod_fil: int, codprod: str) -> ProdutoBuscaOut:
        codigo = codprod.strip()
        if not codigo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe o codigo do produto.")

        produto = None
        oracle_error: Exception | None = None
        try:
            produto = ProtonService(self.db).buscar_produto(cod_fil=cod_fil, codprod=codigo)
        except Exception as exc:
            oracle_error = exc
            produto = None

        if produto is None:
            try:
                produto = self.repository.buscar_produto_legacy(codigo)
            except SQLAlchemyError:
                produto = None

        if produto is None:
            if oracle_error is not None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "Nao foi possivel consultar o Proton/Oracle. "
                        f"{oracle_error.__class__.__name__}: {oracle_error}"
                    ),
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado.")

        return ProdutoBuscaOut(**produto)

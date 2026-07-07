from pydantic import BaseModel, ConfigDict


class PerfilOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    legacy_usuario_id: int | None
    nome: str
    username: str
    email: str | None
    cod_proton: int | None
    perfil: PerfilOut | None
    empresa_padrao_id: int | None
    senha_deve_alterar: bool
    glo_id_user: int
    glo_tp_user: int | None
    glo_empresa: int | None
    glo_id_proton: int | None


class EmpresaAuthOut(BaseModel):
    id: int
    fantasia: str
    cnpj: str | None


class LoginRequest(BaseModel):
    login: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut
    vendedores_filiais_sincronizados: int = 0

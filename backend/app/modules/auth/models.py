from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Perfil(Base):
    __tablename__ = "perfis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_nivel_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_usuario_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(160), index=True)
    cpf: Mapped[str | None] = mapped_column(String(20), index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    cod_proton: Mapped[int | None] = mapped_column(Integer, index=True)
    perfil_id: Mapped[int | None] = mapped_column(ForeignKey("perfis.id"), index=True)
    filial: Mapped[int | None] = mapped_column(Integer)
    empresa_padrao_id: Mapped[int | None] = mapped_column(Integer, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    senha_deve_alterar: Mapped[bool] = mapped_column(Boolean, default=True)

    perfil: Mapped[Perfil | None] = relationship()
    empresas: Mapped[list["UsuarioEmpresa"]] = relationship(back_populates="usuario")

    @property
    def glo_id_user(self) -> int:
        return self.id

    @property
    def glo_tp_user(self) -> int | None:
        return self.perfil_id

    @property
    def glo_empresa(self) -> int | None:
        return self.empresa_padrao_id

    @property
    def glo_id_proton(self) -> int | None:
        return self.cod_proton


class UsuarioEmpresa(Base):
    __tablename__ = "usuarios_empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legacy_usuario_empresa_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), index=True)

    usuario: Mapped[Usuario] = relationship(back_populates="empresas")

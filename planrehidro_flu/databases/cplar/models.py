from typing import Literal

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


TipoHidroRef = Literal["Área de Drenagem", "Nome do Rio", "Desmias Estações"]

SitucaoNavegacao = Literal["Navegação sazonal", "Navegável"]
SitucaoEstudos = Literal["Em desenvolvimento", "Concluído"]
TipoHidrovia = Literal["Canal", "Lago", "Baía", "Rio", "Furo"]

class EstacaoHidroRef(Base):
    __tablename__ = "estacaoes_hidrorreferenciadas"
    __table_args__ = {"schema": "hidrorreferenciamento"}

    codigo: Mapped[int] = mapped_column(primary_key=True)
    area_drenagem: Mapped[float | None]
    nome_rio: Mapped[str]
    cotrecho: Mapped[str]
    cobacia: Mapped[str]
    noriocomp: Mapped[str]
    nuareamont: Mapped[float]
    distancia_m: Mapped[float]
    tipo_href: Mapped[TipoHidroRef]
    
class EstacaoComObjetivos(Base):
    __tablename__ = "estacoes_objetivos_por_area2"
    __table_args__ = {"schema": "objetivos_rhnr"}

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    cobacia_estacao: Mapped[str]
    cobacia_obj: Mapped[str]
    criterio: Mapped[str]
    dist_obj_km: Mapped[float]
    prop_areas: Mapped[float]


class TrechoNavegavel(Base):
    __tablename__ = "hidrorref_trechos_navegaveis"
    __table_args__ = {"schema": "geoft"}
    
    cotrecho: Mapped[int] = mapped_column(primary_key=True)
    cocursodag: Mapped[str]
    cobacia: Mapped[str]
    nome_hidrovia: Mapped[str]
    tipo_hidrovia: Mapped[TipoHidrovia]
    situacao_hidrovia: Mapped[SitucaoNavegacao]
    nome_rio: Mapped[str]
    jurisdicao: Mapped[str]
    regiao_hidrografica: Mapped[str]
    situcao_estudos: Mapped[SitucaoEstudos]

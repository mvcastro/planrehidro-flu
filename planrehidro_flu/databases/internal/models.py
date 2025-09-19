from pathlib import Path

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from planrehidro_flu.databases.hidro.enums import TipoEstacao

print(Path(__file__).parent)
ENGINE = create_engine(f"sqlite:///{Path(__file__).parent / 'database.db'}")


class Base(DeclarativeBase): ...


class InventarioEstacaoFluAna(Base):
    __tablename__ = "inventario_estacoes_flu_ana"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str | None]
    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude: Mapped[float | None]
    area_drenagem_km2: Mapped[float | None]
    bacia: Mapped[str]
    subbacia: Mapped[str]
    rio: Mapped[str | None]
    estado: Mapped[str]
    municipio: Mapped[str]
    responsavel: Mapped[str]
    tipo_estacao: Mapped[TipoEstacao]
    estacao_telemetrica: Mapped[bool]
    operando: Mapped[bool]


class GrupoCriterios(Base):
    __tablename__ = "grupo_criterios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    grupo: Mapped[str] = mapped_column(unique=True)


class DescricaoCriterio(Base):
    __tablename__ = "descricao_criterio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo_criterios.id"))
    nome_campo: Mapped[str] = mapped_column(unique=True)
    descricao_criterio: Mapped[str] = mapped_column(unique=True)
    unidade: Mapped[str]


class CriteriosDaEstacao(Base):
    __tablename__ = "valor_criterio"

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    area_dren: Mapped[float]
    espacial: Mapped[float]
    cheias: Mapped[bool]
    ish: Mapped[str]
    semiarido: Mapped[bool]
    irrigacao: Mapped[bool]
    rhnr: Mapped[str]
    navegacao: Mapped[bool]
    extensao: Mapped[int]
    desv_cchave: Mapped[float]
    med_desc: Mapped[float]

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
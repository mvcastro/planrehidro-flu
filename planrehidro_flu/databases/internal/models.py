from pathlib import Path

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from planrehidro_flu.databases.hidro.enums import TipoEstacao

print(Path(__file__).parent)
ENGINE = create_engine(f"sqlite:///{Path(__file__).parent / 'database.db'}")


class Base(DeclarativeBase): ...


class InventarioEstacoesFluAna(Base):
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
    __tablename__ = "criterio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo_criterios.id"))
    criterio: Mapped[str] = mapped_column(unique=True)
    unidade: Mapped[str]


class ValorCriterio(Base):
    __tablename__ = "valor_criterio"

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    criterio_id: Mapped[int] = mapped_column(
        ForeignKey("criterio.id"), primary_key=True
    )
    valor_numero: Mapped[float] = mapped_column(nullable=True)
    valor_string: Mapped[str] = mapped_column(nullable=True)


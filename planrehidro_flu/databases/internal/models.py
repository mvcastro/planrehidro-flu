from pathlib import Path

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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

    criterios: Mapped["Criterio"] = relationship(back_populates="grupo")


class Criterio(Base):
    __tablename__ = "criterio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)   
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupo_criterios.id"))
    criterio: Mapped[str] = mapped_column(unique=True)
    unidade: Mapped[str]

    grupo: Mapped["GrupoCriterios"] = relationship(back_populates="criterios")
    valores_criterio: Mapped["ValorCriterio"] = relationship(back_populates="criterio")


class ValorCriterio(Base):
    __tablename__ = "valor_criterio"

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    criterio_id: Mapped[int] = mapped_column(ForeignKey("criterio.id"), primary_key=True)
    valor: Mapped[float]

    criterio: Mapped["Criterio"] = relationship(back_populates="valores_criterio")

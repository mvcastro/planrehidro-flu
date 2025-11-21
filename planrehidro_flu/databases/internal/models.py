from pathlib import Path

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ENGINE = create_engine(f"sqlite:///{Path(__file__).parent / 'database.db'}")


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class InventarioEstacaoFluAna(Base):
    __tablename__ = "inventario_estacoes_flu_ana"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str | None]
    latitude: Mapped[float]
    longitude: Mapped[float]
    area_drenagem_km2: Mapped[float | None]
    bacia_codigo: Mapped[int]
    subbacia_codigo: Mapped[int]
    responsavel_codigo: Mapped[int]
    operadora: Mapped[int]
    operadora_regional: Mapped[str] = mapped_column(nullable=True)


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
    area_dren: Mapped[float] = mapped_column(nullable=True)
    espacial: Mapped[float] = mapped_column(nullable=True)
    cheias: Mapped[bool] = mapped_column(nullable=True)
    ish: Mapped[str] = mapped_column(nullable=True)
    semiarido: Mapped[bool] = mapped_column(nullable=True)
    irrigacao: Mapped[bool] = mapped_column(nullable=True)
    navegacao: Mapped[bool] = mapped_column(nullable=True)
    extensao: Mapped[int] = mapped_column(nullable=True)
    desv_cchave: Mapped[float] = mapped_column(nullable=True)
    med_desc: Mapped[float] = mapped_column(nullable=True)
    est_energia: Mapped[float] = mapped_column(nullable=True)
    rhnr_c1: Mapped[float] = mapped_column(nullable=True)
    rhnr_c2: Mapped[float] = mapped_column(nullable=True)


class Operadora(Base):
    __tablename__ = "operadora"

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    operadora_codigo: Mapped[int]
    operadora_unidade: Mapped[int]
    operadora_subunidade: Mapped[int]


class RegiaoHidrografica(Base):
    __tablename__ = "regioes_hidrograficas"

    rhi_cd: Mapped[int] = mapped_column(primary_key=True)
    rhi_sg: Mapped[str] = mapped_column(unique=True)
    rhi_nm: Mapped[str] = mapped_column(unique=True)


class EstacaoFluPorRH(Base):
    __tablename__ = "estacoes_flu_por_rh"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    rhi_cd: Mapped[int] = mapped_column(ForeignKey("regioes_hidrograficas.rhi_cd"))
    

class CenarioEstacaoesRHNR(Base):
    __tablename__ = "cenario_estacaoes_rhnr"
        
    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    cenario1: Mapped[bool] = mapped_column(nullable=False)
    cenario2: Mapped[bool] = mapped_column(nullable=False)




from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from planrehidro_flu.databases.hidro.enums import TipoDaEstacao


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Estacao(Base):
    __tablename__ = "Estacao"

    Registroid: Mapped[int] = mapped_column(primary_key=True)
    Importado: Mapped[int]
    Temporario: Mapped[int]
    Removido: Mapped[int]
    ImportadoRepetido: Mapped[int]
    Codigo: Mapped[int]
    Nome: Mapped[str]
    Latitude: Mapped[float]
    Longitude: Mapped[float]
    Altitude: Mapped[float]
    AreaDrenagem: Mapped[float]
    BaciaCodigo: Mapped[int] = mapped_column(ForeignKey("Bacia.Codigo"))
    SubBaciaCodigo: Mapped[int] = mapped_column(ForeignKey("SubBacia.Codigo"))
    RioCodigo: Mapped[int] = mapped_column(ForeignKey("Rio.Codigo"))
    EstadoCodigo: Mapped[int] = mapped_column(ForeignKey("Estado.Codigo"))
    MunicipioCodigo: Mapped[int] = mapped_column(ForeignKey("Municipio.Codigo"))
    ResponsavelCodigo: Mapped[int] = mapped_column(ForeignKey("Entidade.Codigo"))
    OperadoraCodigo: Mapped[int] = mapped_column(ForeignKey("Entidade.Codigo"))
    TipoEstacao: Mapped[int]
    TipoEstacaoTelemetrica: Mapped[int]
    TipoRedeEnergetica: Mapped[int]
    Operando: Mapped[int]
    Descricao: Mapped[str]


    bacia: Mapped["Bacia"] = relationship(back_populates="estacao")


class Bacia(Base):
    __tablename__ = "Bacia"

    Registroid: Mapped[int] = mapped_column(primary_key=True)
    Codigo: Mapped[int]
    Nome: Mapped[str]
    Sigla: Mapped[str]

    estacao: Mapped[list["Estacao"]] = relationship(back_populates="bacia")


class SubBacia(Base):
    __tablename__ = "SubBacia"

    Registroid: Mapped[int] = mapped_column(primary_key=True)
    Codigo: Mapped[int]
    Nome: Mapped[str]
    Jurisdicao: Mapped[int] = mapped_column(ForeignKey("Entidade.Codigo"))
    BaciaCodigo: Mapped[int] = mapped_column(ForeignKey("Bacia.Codigo"))


class Entidade(Base):
    __tablename__ = "Entidade"

    Registroid: Mapped[int] = mapped_column(primary_key=True)
    Codigo: Mapped[int]
    Nome: Mapped[str]
    Sigla: Mapped[str]


class Rio(Base):
    __tablename__ = "Rio"

    Registroid: Mapped[int] = mapped_column(primary_key=True)
    Codigo: Mapped[int]
    Nome: Mapped[str]
    Jurisdicao: Mapped[int] = mapped_column(ForeignKey("Entidade.Codigo"))
    BaciaCodigo: Mapped[int] = mapped_column(ForeignKey("Bacia.Codigo"))
    SubBaciaCodigo: Mapped[int] = mapped_column(ForeignKey("SubBacia.Codigo"))


class Estado(Base):
    __tablename__ = "Estado"

    Registroid: Mapped[int] = mapped_column(primary_key=True)
    Codigo: Mapped[int]
    CodigoIBGE: Mapped[int]
    Sigla: Mapped[str]
    Nome: Mapped[str]


class Municipio(Base):
    __tablename__ = "Municipio"

    RegistroId: Mapped[int] = mapped_column(primary_key=True)
    Codigo: Mapped[int]
    CodigoIBGE: Mapped[int]
    Nome: Mapped[str]
    EstadoCodigo: Mapped[int] = mapped_column(ForeignKey("Estado.Codigo"))


class PivotChuva(Base):
    __tablename__ = "PivotChuva"

    RegistroID: Mapped[int] = mapped_column(primary_key=True)
    EstacaoCodigo: Mapped[int] = mapped_column(ForeignKey("Estacao.Codigo"))
    NivelConsistencia: Mapped[int]
    Data: Mapped[date]
    Chuva: Mapped[float]
    Status: Mapped[int]


@dataclass
class StationAttribs:
    BaciaCodigo: Optional[int]
    SubBaciaCodigo: Optional[int]
    RioCodigo: Optional[int]
    EstadoCodigo: Optional[int]
    MunicipioCodigo: Optional[int]
    ResponsavelCodigo: Optional[int]
    ResponsavelUnidade: Optional[int]
    ResponsavelJurisdicao: Optional[int]
    OperadoraCodigo: Optional[int]
    OperadoraUnidade: Optional[int]
    OperadoraSubUnidade: Optional[int]
    TipoEstacao: TipoDaEstacao
    Codigo: float
    Nome: Optional[str]
    CodigoAdicional: Optional[str]
    Latitude: float
    Longitude: float
    Altitude: Optional[float]
    AreaDrenagem: Optional[float]
    TipoEstacaoEscala: Optional[int]
    TipoEstacaoRegistradorNivel: Optional[int]
    TipoEstacaoDescLiquida: Optional[int]
    TipoEstacaoSedimentos: Optional[int]
    TipoEstacaoQualAgua: Optional[int]
    TipoEstacaoPluviometro: Optional[int]
    TipoEstacaoRegistradorChuva: Optional[int]
    TipoEstacaoTanqueEvapo: Optional[int]
    TipoEstacaoClimatologica: Optional[int]
    TipoEstacaoPiezometria: Optional[int]
    TipoEstacaoTelemetrica: Optional[int]
    PeriodoEscalaInicio: Optional[date]
    PeriodoEscalaFim: Optional[date]
    PeriodoRegistradorNivelInicio: Optional[date]
    PeriodoRegistradorNivelFim: Optional[date]
    PeriodoDescLiquidaInicio: Optional[date]
    PeriodoDescLiquidaFim: Optional[date]
    PeriodoSedimentosInicio: Optional[date]
    PeriodoSedimentosFim: Optional[date]
    PeriodoQualAguaInicio: Optional[date]
    PeriodoQualAguaFim: Optional[date]
    PeriodoPluviometroInicio: Optional[date]
    PeriodoPluviometroFim: Optional[date]
    PeriodoRegistradorChuvaInicio: Optional[date]
    PeriodoRegistradorChuvaFim: Optional[date]
    PeriodoTanqueEvapoInicio: Optional[date]
    PeriodoTanqueEvapoFim: Optional[date]
    PeriodoClimatologicaInicio: Optional[date]
    PeriodoClimatologicaFim: Optional[date]
    PeriodoPiezometriaInicio: Optional[date]
    PeriodoPiezometriaFim: Optional[date]
    PeriodoTelemetricaInicio: Optional[date]
    PeriodoTelemetricaFim: Optional[date]
    TipoRedeBasica: Optional[int]
    TipoRedeEnergetica: Optional[int]
    TipoRedeNavegacao: Optional[int]
    TipoRedeCursoDagua: Optional[int]
    TipoRedeEstrategica: Optional[int]
    TipoRedeCaptacao: Optional[int]
    TipoRedeSedimentos: Optional[int]
    TipoRedeQualAgua: Optional[int]
    TipoRedeClasseVazao: Optional[int]
    UltimaAtualizacao: Optional[int]
    Operando: Optional[int]


class ResumoDescarga(Base):
    __tablename__ = "ResumoDescarga"

    RegistroID: Mapped[int] = mapped_column(primary_key=True)
    Importado: Mapped[int]
    Temporario: Mapped[int]
    Removido: Mapped[int]
    ImportadoRepetido: Mapped[int]
    EstacaoCodigo: Mapped[int]
    NivelConsistencia: Mapped[int]
    Data: Mapped[date]
    Cota: Mapped[float]
    Vazao: Mapped[float | None]
    AreaMolhada: Mapped[float | None]
    Largura: Mapped[float | None]
    VelMedia: Mapped[float | None]
    Profundidade: Mapped[float | None]


class CurvaDescarga(Base):
    __tablename__ = "CurvaDescarga"

    RegistroID: Mapped[int] = mapped_column(primary_key=True)
    Importado: Mapped[int]
    Temporario: Mapped[int]
    Removido: Mapped[int]
    ImportadoRepetido: Mapped[int]
    EstacaoCodigo: Mapped[int]
    NivelConsistencia: Mapped[int]
    PeriodoValidadeInicio: Mapped[date]
    PeriodoValidadeFim: Mapped[date]
    CotaMaxima: Mapped[float]
    CotaMinima: Mapped[float]
    TipoCurva: Mapped[int]
    TipoEquacao: Mapped[int]
    CoefA: Mapped[float]
    CoefH0: Mapped[float]
    CoefN: Mapped[float]
    CoefA0: Mapped[float]
    CoefA1: Mapped[float]
    CoefA2: Mapped[float]
    CoefA3: Mapped[float]


class PivotVazao(Base):
    __tablename__ = "PivotVazao"

    RegistroID: Mapped[int] = mapped_column(primary_key=True)
    EstacaoCodigo: Mapped[int]
    Data: Mapped[date]
    NivelConsistencia: Mapped[int]
    Vazao: Mapped[float]


class PivotCota(Base):
    __tablename__ = "PivotCota"

    RegistroID: Mapped[int] = mapped_column(primary_key=True)
    CotaID: Mapped[int]
    EstacaoCodigo: Mapped[int]
    NivelConsistencia: Mapped[int]
    Data: Mapped[date]
    Cota: Mapped[float]
    Status: Mapped[int]

from datetime import date
from typing import Literal

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


TipoHidroRef = Literal["Área de Drenagem", "Nome do Rio", "Demais Estações"]

SitucaoNavegacao = Literal["Navegação sazonal", "Navegável"]
SitucaoEstudos = Literal["Em desenvolvimento", "Concluído"]
TipoHidrovia = Literal["Canal", "Lago", "Baía", "Rio", "Furo"]


class EstacaoFlu(Base):
    __tablename__ = "estacao_flu"
    __table_args__ = {"schema": "estacoes"}

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    codigo_adicional: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude: Mapped[float]
    area_drenagem: Mapped[float | None]
    bacia_codigo: Mapped[int]
    subbacia_codigo: Mapped[int]
    estado_codigo: Mapped[int]
    municipio_codigo: Mapped[int]
    ultima_atualizacao: Mapped[date]
    operando: Mapped[int]
    descricao: Mapped[str]
    historico: Mapped[str]


class Responsavel(Base):
    __tablename__ = "responsavel"
    __table_args__ = {"schema": "estacoes"}

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    responsavel_codigo: Mapped[int]
    responsavel_unidade: Mapped[int]
    responsavel_jurisdicao: Mapped[int]


class Operadora(Base):
    __tablename__ = "operadora"
    __table_args__ = {"schema": "estacoes"}

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    operadora_codigo: Mapped[int]
    operadora_unidade: Mapped[int]
    operadora_subunidade: Mapped[int]


class EstacaoHidroRefBHO2013(Base):
    __tablename__ = "estacoes_hidrorreferenciadas_bho2013"
    __table_args__ = {"schema": "hidrorref_bho2013"}

    codigo: Mapped[int] = mapped_column(primary_key=True)
    area_drenagem: Mapped[float | None]
    nome_rio: Mapped[str]
    cotrecho: Mapped[str]
    cocursodag: Mapped[str]
    cobacia: Mapped[str]
    noriocomp: Mapped[str]
    nuareamont: Mapped[float]
    distancia_m: Mapped[float]
    tipo_href: Mapped[TipoHidroRef]


class EstacaoHidroRefBHAE(Base):
    __tablename__ = "estacoes_hidrorreferenciadas_bhae"
    __table_args__ = {"schema": "hidrorref_bhae"}

    codigo: Mapped[int] = mapped_column(primary_key=True)
    area_drenagem: Mapped[float | None]
    nome_rio: Mapped[str]
    cotrecho: Mapped[str]
    cocursodag: Mapped[str]
    cobacia: Mapped[str]
    noriocomp: Mapped[str]
    nuareamont: Mapped[float]
    distancia_m: Mapped[float]
    tipo_href: Mapped[TipoHidroRef]


class EstacaoComObjetivos(Base):
    __tablename__ = "estacoes_objetivos_por_area2"
    __table_args__ = {"schema": "objetivos_rhnr"}

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    cobacia_estacao: Mapped[str] = mapped_column(primary_key=True)
    cobacia_obj: Mapped[str] = mapped_column(primary_key=True)
    criterio: Mapped[str] = mapped_column(primary_key=True)
    dist_obj_km: Mapped[float]
    prop_areas: Mapped[float]


class TrechoNavegavel(Base):
    __tablename__ = "hidrorref_trechos_navegaveis"
    __table_args__ = {"schema": "hidrorref_bho2013"}

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


class TrechoVulneravelACheias(Base):
    __tablename__ = "geoft_hidrorref_inundacoes"
    __table_args__ = {"schema": "hidrorref_bho2013"}

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[int]
    cobacia: Mapped[str]
    inund_id: Mapped[int]
    inund_noriocomp: Mapped[str]
    inund_frequencia: Mapped[int]
    inund_impacto: Mapped[int]
    inund_vulnerabilidade: Mapped[int]
    inund_cd_mun: Mapped[str]
    inund_nome_mun: Mapped[str]


class PoloNacional(Base):
    __tablename__ = "polos_nacionais_2021"
    __table_args__ = {"schema": "geoft"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    polo_irrig: Mapped[str]
    tipologia: Mapped[str]
    id2: Mapped[float]
    shape_leng: Mapped[float]
    shape_area: Mapped[float]


class IndiceSegurancaHidrica(Base):
    __tablename__ = "indice_seguranca_hidrica_2017_area"
    __table_args__ = {"schema": "geoft"}

    id: Mapped[int] = mapped_column(primary_key=True)
    cobacia: Mapped[str]
    ecossistema: Mapped[str]
    humana: Mapped[str]
    economica: Mapped[str]
    resiliencia: Mapped[str]
    brasil: Mapped[str]
    nuareacont: Mapped[float]
    nuareamont: Mapped[float]


class IndiceSegurancaHidricaNumerico(Base):
    __tablename__ = "pnsh_ish"
    __table_args__ = {"schema": "ish"}

    ire_cobacia: Mapped[str] = mapped_column(primary_key=True)
    ire_cs_ambiental: Mapped[float]
    ire_cs_humano: Mapped[float]
    ire_cs_economico: Mapped[float]
    ire_cs_resiliencia: Mapped[float]
    ire_cs_ishfinal: Mapped[float] = mapped_column(nullable=False)
    ire_nuareacont: Mapped[float] = mapped_column(nullable=False)
    ire_nuareamont: Mapped[float] = mapped_column(nullable=False)


class EstacaoRHNRSelecaoInicial(Base):
    __tablename__ = "estacoes_rhnr_selecao_inicial"
    __table_args__ = {"schema": "revisao_rhnr"}

    codigo: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    objetivo1: Mapped[int] = mapped_column(SmallInteger)
    objetivo2: Mapped[int] = mapped_column(SmallInteger)
    objetivo3: Mapped[int] = mapped_column(SmallInteger)
    objetivo4: Mapped[int] = mapped_column(SmallInteger)
    objetivo5: Mapped[int] = mapped_column(SmallInteger)
    objetivo6: Mapped[int] = mapped_column(SmallInteger)


class EstacaoPropostaRHNR(Base):
    __tablename__ = "estacoes_proposta_rhnr"
    __table_args__ = {"schema": "revisao_rhnr"}

    codigo: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    tipo_estacao: Mapped[str] = mapped_column(String(5), nullable=False)
    proposta_operacao_planilha: Mapped[str] = mapped_column(nullable=True)
    proposta_tipo: Mapped[str] = mapped_column(String(5), nullable=True)
    proposta_integra_rhnr: Mapped[bool] = mapped_column(nullable=True)
    observacao: Mapped[str] = mapped_column(nullable=True)
    proposta_operacao: Mapped[str] = mapped_column(nullable=True)

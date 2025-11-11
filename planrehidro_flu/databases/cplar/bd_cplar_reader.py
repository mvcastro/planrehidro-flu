import os
from operator import and_
from typing import Sequence, cast

import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import case, create_engine, or_, select, text
from sqlalchemy.orm import Session

from planrehidro_flu.databases.cplar.models import (
    EstacaoComObjetivos,
    EstacaoFlu,
    EstacaoHidroRefBHAE,
    EstacaoHidroRefBHO2013,
    EstacaoPropostaRHNR,
    EstacaoRHNRSelecaoInicial,
    IndiceSegurancaHidrica,
    IndiceSegurancaHidricaNumerico,
    Operadora,
    PoloNacional,
    Responsavel,
    TrechoNavegavel,
    TrechoVulneravelACheias,
)
from planrehidro_flu.databases.hidro.enums import ResponsavelEnum

load_dotenv()


def cobacia_to_cocursodag(cobacia: str) -> str:
    for idx, char in enumerate(cobacia[::-1]):
        if int(char) % 2 == 0:
            if idx == 0:
                return cobacia
            return cobacia[:-idx]
    raise ValueError("Cobacia inválido")


def localiza_cocursodags_de_jusante(cobacia: str) -> list[str]:
    cocursodags = []
    for idx, _ in enumerate(cobacia, start=1):
        if int(cobacia[:idx]) % 2 == 0:
            cocursodags.append(cobacia[:idx])
    return cocursodags


class PostgresReader:
    def __init__(self) -> None:
        db_name = os.getenv("POSTGRES_DB_NAME")
        user = os.getenv("POSTGRES_DB_USER")
        password = os.getenv("POSTGRES_DB_PASSWORD")
        host = os.getenv("POSTGRES_DB_HOST")
        port = os.getenv("POSTGRES_DB_PORT")
        connection_url = (
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
        )
        self.engine = create_engine(connection_url)

    def retorna_estacao_hidrorreferenciada[
        T: (EstacaoHidroRefBHO2013, EstacaoHidroRefBHAE)
    ](
        self,
        classe_href: type[T],
        codigo_estacao: int,
    ) -> T:
        with Session(self.engine) as session:
            query = select(classe_href).where(classe_href.codigo == codigo_estacao)
            response = session.execute(query).scalar()

            if not response:
                raise ValueError(
                    f"Estação Hidrorreferenciada com código {codigo_estacao} não encontrada."
                )
        return response

    def retorna_estacoes_hidrorreferenciadas_de_montante[
        T: (EstacaoHidroRefBHO2013, EstacaoHidroRefBHAE)
    ](self, classe_href: type[T], cobacia: str) -> list[T]:
        cocursodag = cobacia_to_cocursodag(cobacia=cobacia)
        with Session(self.engine) as session:
            query = select(classe_href).where(
                classe_href.cobacia >= cobacia,
                classe_href.cocursodag.like(f"{cocursodag}%%"),
            )
            response = session.execute(query).scalars().all()

        result = [estacao for estacao in response if estacao.area_drenagem is not None]

        return result

    def retorna_estacoes_hidrorreferenciadas_de_jusante[
        T: (EstacaoHidroRefBHO2013, EstacaoHidroRefBHAE)
    ](self, classe_href: type[T], cobacia: str) -> list[T]:
        cocursodags = localiza_cocursodags_de_jusante(cobacia=cobacia)
        with Session(self.engine) as session:
            query = select(classe_href).where(
                classe_href.cobacia < cobacia,
                classe_href.cocursodag.in_(cocursodags),
            )
            response = session.execute(query).scalars().all()

        return [estacao for estacao in response if estacao.area_drenagem is not None]

    def retorna_trecho_navegavel(self, cobacia: str) -> TrechoNavegavel | None:
        with Session(self.engine) as session:
            query = select(TrechoNavegavel).where(TrechoNavegavel.cobacia == cobacia)
            response = session.execute(query).scalar()
        return response

    def retorna_trecho_vulneravel_a_cheias(
        self, cobacia: str
    ) -> TrechoVulneravelACheias | None:
        with Session(self.engine) as session:
            query = select(TrechoVulneravelACheias).where(
                TrechoVulneravelACheias.cobacia == cobacia
            )
            response = session.execute(query).scalar()
        return response

    def retorna_geometria_semiarido(self) -> gpd.GeoSeries:
        query = "SELECT * FROM geoft.semiarido_2024"
        gdf = gpd.read_postgis(query, self.engine, geom_col="geom")
        return gdf.geometry

    def esta_no_semiarido(self, latitude: float, longitude: float) -> bool:
        query = text("""
            SELECT * FROM geoft.semiarido_2024
            WHERE ST_Intersects(geom, ST_Point(:longitude, :latitude, 4674)) 
        """)

        with Session(self.engine) as session:
            response = session.execute(
                query, {"longitude": longitude, "latitude": latitude}
            ).first()

        return False if response is None else True

    def retorna_objetivos_rhnr(
        self, codigo_estacao: int
    ) -> Sequence[EstacaoComObjetivos]:
        with Session(self.engine) as session:
            query = select(EstacaoComObjetivos).where(
                EstacaoComObjetivos.codigo_estacao == codigo_estacao
            )
            response = session.execute(query).scalars().all()
        return response

    def retorna_estacoes_de_montante[T: (EstacaoHidroRefBHO2013, EstacaoHidroRefBHAE)](
        self, classe_href: type[T], estacao_href: T
    ) -> Sequence[T]:
        with Session(self.engine) as session:
            query1 = (
                select(classe_href)
                .join(EstacaoFlu, EstacaoFlu.codigo == classe_href.codigo)
                .join(Responsavel, Responsavel.codigo_estacao == EstacaoFlu.codigo)
                .where(
                    EstacaoFlu.operando == 1,
                    Responsavel.responsavel_codigo == ResponsavelEnum.ANA,
                    classe_href.cobacia >= estacao_href.cobacia,
                    classe_href.codigo != estacao_href.codigo,
                    classe_href.area_drenagem <= estacao_href.area_drenagem,
                    classe_href.cocursodag.like(f"{estacao_href.cocursodag}%%"),
                    # classe_href.area_drenagem.is_not(None),
                    or_(
                        EstacaoFlu.descricao.not_like("%%HIDROOBSERVA%%"),
                        EstacaoFlu.descricao.is_(None),
                    ),
                )
            )

            query2 = (
                select(classe_href)
                .join(EstacaoFlu, EstacaoFlu.codigo == classe_href.codigo)
                .join(Responsavel, Responsavel.codigo_estacao == EstacaoFlu.codigo)
                .join(Operadora, Operadora.codigo_estacao == EstacaoFlu.codigo)
                .where(
                    EstacaoFlu.operando == 1,
                    EstacaoFlu.descricao.like("%%HIDROOBSERVA%%"),
                    Responsavel.responsavel_codigo == ResponsavelEnum.ANA,
                    Operadora.operadora_codigo == ResponsavelEnum.SGB_CPRM,
                    classe_href.cobacia >= estacao_href.cobacia,
                    classe_href.cocursodag.like(f"{estacao_href.cocursodag}%%"),
                    classe_href.codigo != estacao_href.codigo,
                    classe_href.area_drenagem <= estacao_href.area_drenagem,
                    # classe_href.area_drenagem.is_not(None),
                )
            )
            response1 = session.execute(query1).scalars().all()
            response2 = session.execute(query2).scalars().all()

        return [
            estacao
            for estacao in list(response1) + list(response2)
            # if cast(float, estacao.area_drenagem)
            # <= cast(float, estacao_href.area_drenagem)
        ]

    def retorno_polo_nacional_por_corrdenadas(
        self, latitude: float, longitude: float
    ) -> PoloNacional | None:
        query = text("""
            SELECT * FROM geoft.polos_nacionais_2021
            WHERE ST_Intersects(geom, ST_Point(:longitude, :latitude, 4674)) 
        """)

        with Session(self.engine) as session:
            response = session.execute(
                query, {"longitude": longitude, "latitude": latitude}
            ).scalar()

        return cast(PoloNacional, response)

    def retorna_classes_ish_por_area_drenagem(
        self, cobacia: str
    ) -> Sequence[IndiceSegurancaHidrica]:
        cocursodag = cobacia_to_cocursodag(cobacia)

        query = select(IndiceSegurancaHidrica).where(
            IndiceSegurancaHidrica.cobacia >= cobacia,
            IndiceSegurancaHidrica.cobacia.like(f"{cocursodag}%%"),
        )
        with Session(self.engine) as session:
            response = session.execute(query).scalars().all()

        return response

    def retorna_classes_ish_numerico_por_area_drenagem(
        self, cobacia: str
    ) -> Sequence[IndiceSegurancaHidricaNumerico]:
        cocursodag = cobacia_to_cocursodag(cobacia)

        query = select(IndiceSegurancaHidricaNumerico).where(
            IndiceSegurancaHidricaNumerico.ire_cobacia >= cobacia,
            IndiceSegurancaHidricaNumerico.ire_cobacia.like(f"{cocursodag}%%"),
        )
        with Session(self.engine) as session:
            response = session.execute(query).scalars().all()

        return response

    def retorna_estacoes_rhnr_selecao_inicial(self) -> Sequence[EstacaoFlu]:
        with Session(self.engine) as session:
            response = (
                session.execute(
                    select(EstacaoFlu).where(
                        EstacaoFlu.codigo == EstacaoRHNRSelecaoInicial.codigo,
                    )
                )
                .scalars()
                .all()
            )
        return response

    def retorna_estacoes_implementadas_rhnr(self) -> Sequence[EstacaoFlu]:
        with Session(self.engine) as session:
            response = (
                session.execute(
                    select(EstacaoFlu).where(EstacaoFlu.descricao.like("%RHNR%"))
                )
                .scalars()
                .all()
            )

        return response

    def retorna_estacoes_propostas_rhnr(self) -> Sequence[EstacaoFlu]:
        with Session(self.engine) as session:
            response = (
                session.execute(
                    select(EstacaoFlu).where(
                        EstacaoFlu.codigo == EstacaoPropostaRHNR.codigo,
                        EstacaoPropostaRHNR.proposta_integra_rhnr.is_(True),
                    )
                )
                .scalars()
                .all()
            )
        return response

    def retorna_estacoes_rhnr_cenario1(self) -> list[EstacaoFlu]:
        """
        Retorna as estações RHNR do cenário 1:
        Seleção Inicial + Estações Implementadas + Estações da Revisaõ para Integrar a RHNR.
        """
        response1 = self.retorna_estacoes_rhnr_selecao_inicial()
        response2 = self.retorna_estacoes_implementadas_rhnr()
        response3 = self.retorna_estacoes_propostas_rhnr()
        data = list(response1) + list(response2) + list(response3)

        seen_ids = set()
        unique_records = []
        for record in data:
            if record.codigo not in seen_ids:
                unique_records.append(record)
                seen_ids.add(record.codigo)

        return unique_records

    def retorna_estacoes_rhnr_cenario2(self) -> list[EstacaoFlu]:
        """
        Retorna as estações RHNR do cenário 2:
        Apenas Estações Propostas para Integrar a RHNR.
        """
        return list(self.retorna_estacoes_propostas_rhnr())

    def retorna_dados_adicionais_estacoes(self) -> pd.DataFrame:
        with Session(self.engine) as session:
            response = session.execute(
                select(
                    EstacaoFlu.codigo,
                    EstacaoFlu.bacia_codigo,
                    EstacaoFlu.subbacia_codigo,
                    Responsavel.responsavel_codigo,
                    Operadora.operadora_codigo,
                    case(
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade in (1, 2),
                            ),
                            "PORTO VELHO - REPO",
                        ),  # RONDÔNIA - ACRE / REPO
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 3,
                            ),
                            "MANAUS - SUREG-MA",
                        ),  # AMAZONAS / SUREG-MA
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 5,
                            ),
                            "BELEM - SUREG-BR",
                        ),  # PA / SUREG-BE
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 8,
                            ),
                            "TERESINA - RETE",
                        ),  # PI / RETE
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 9,
                            ),
                            "FORTALEZA - REFO",
                        ),  # CEARÁ / REFO
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 12,
                            ),
                            "RECIFE - SUREG-RE",
                        ),  # PE / SUREG-RE
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 16,
                            ),
                            "SALVADOR - SUREG-SA",
                        ),  # BA / SUREG-SA
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 17,
                            ),
                            "BELO HORIZONTE - SUREG-BH",
                        ),  # MG / SUREG-BH
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 19,
                            ),
                            "RIO DE JANEIRO - ERJ",
                        ),  # RJ / ERJ
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 21,
                            ),
                            "SÃO PAULO - SUREG-SP",
                        ),  # SP / SUREG-SP
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 24,
                            ),
                            "PORTO ALEGRE - SUREG-PA",
                        ),  # RIO GRANDE DO SUL / SUREG-PA
                        (
                            and_(
                                Operadora.operadora_codigo == 82,
                                Operadora.operadora_unidade == 26,
                            ),
                            "GOIÂNIA - SUREG-GO",
                        ),  # GOÍAS / SUREG-GO
                        else_=None,
                    ).label("operadora_regional"),
                    Operadora.operadora_unidade,
                )
                .join(Responsavel, Responsavel.codigo_estacao == EstacaoFlu.codigo)
                .join(Operadora, Operadora.codigo_estacao == EstacaoFlu.codigo)
            )
            
        return pd.DataFrame([row._asdict() for row in response])

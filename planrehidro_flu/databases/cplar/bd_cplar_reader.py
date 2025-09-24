import os
from typing import Sequence, cast

import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from planrehidro_flu.databases.cplar.models import (
    EstacaoComObjetivos,
    EstacaoFlu,
    EstacaoHidroRef,
    IndiceSegurancaHidrica,
    IndiceSegurancaHidricaNumerico,
    PoloNacional,
    TrechoNavegavel,
    TrechoVulneravelACheias,
)

load_dotenv()


def cobacia_to_cocursodag(cobacia: str) -> str:
    for idx, char in enumerate(cobacia[::-1]):
        if int(char) % 2 == 0:
            if idx == 0:
                return cobacia
            return cobacia[:-idx]
    raise ValueError("Cobacia inválido")


def localiza_cocursodags_de_jusante(cobacia: str) -> list[str]:
    cobacias = []
    for idx, _ in enumerate(cobacia, start=1):
        if int(cobacia[:idx]) % 2 == 0:
            cobacias.append(cobacia[:idx])
    return cobacias


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

    def retorna_estacao_hidrorreferenciada(
        self, codigo_estacao: int
    ) -> EstacaoHidroRef:
        with Session(self.engine) as session:
            query = select(EstacaoHidroRef).where(
                EstacaoHidroRef.codigo == codigo_estacao
            )
            response = session.execute(query).scalar()

        if not response:
            raise ValueError(
                f"Estação Hidrorreferenciada com código {codigo_estacao} não encontrada."
            )
        return response

    def retorna_estacoes_hidrorreferenciadas_de_montante(
        self, cobacia: str, area_drenagem: float, limiar_proporcao: float = 0.1
    ) -> list[EstacaoHidroRef]:
        cocursodag = cobacia_to_cocursodag(cobacia=cobacia)
        with Session(self.engine) as session:
            query = select(EstacaoHidroRef).where(
                EstacaoHidroRef.cobacia > cobacia,
                EstacaoHidroRef.cocursodag.like(f"{cocursodag}%%"),
            )
            response = session.execute(query).scalars().all()

        return [
            estacao
            for estacao in response
            if estacao.area_drenagem is not None
            and abs(1 - (estacao.area_drenagem / area_drenagem)) <= limiar_proporcao
        ]

    def retorna_estacoes_hidrorreferenciadas_de_jusante(
        self, cobacia: str, area_drenagem: float, limiar_proporcao: float = 0.1
    ) -> list[EstacaoHidroRef]:
        cocursodags = localiza_cocursodags_de_jusante(cobacia=cobacia)
        with Session(self.engine) as session:
            query = select(EstacaoHidroRef).where(
                EstacaoHidroRef.cobacia < cobacia,
                EstacaoHidroRef.cocursodag.in_(cocursodags),
            )
            response = session.execute(query).scalars().all()

        return [
            estacao
            for estacao in response
            if estacao.area_drenagem is not None
            and abs(1 - (estacao.area_drenagem / area_drenagem)) <= limiar_proporcao
        ]

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

    def retorna_estacoes_de_montante(self, cobacia: str) -> list[EstacaoFlu]:
        cocursodag = cobacia_to_cocursodag(cobacia)

        query = text("""
            WITH area_drenagem AS (
                SELECT geom
                FROM geoft.bho_2013_areacontribuicao
                WHERE cobacia >= :cobacia 
                AND cocursodag LIKE CONCAT(:cocursodag, '%%')
            )
            SELECT * FROM estacoes.estacao_flu
            INNER JOIN area_drenagem
            ON ST_Intersects(estacao_flu.geom, area_drenagem.geom)
        """)

        with Session(self.engine) as session:
            response = (
                session.execute(query, {"cobacia": cobacia, "cocursodag": cocursodag})
                .scalars()
                .all()
            )

        return cast(list[EstacaoFlu], response)

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

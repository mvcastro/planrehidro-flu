import os
import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from planrehidro_flu.databases.cplar.models import EstacaoComObjetivos, EstacaoHidroRef, TrechoNavegavel

load_dotenv()


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
    
    def existe_trecho_navegavel(self, cobacia: str) -> TrechoNavegavel | None:
        with Session(self.engine) as session:
            query = select(TrechoNavegavel).where(
                TrechoNavegavel.cobacia == cobacia
            )
            response = session.execute(query).scalar()

        return response
    
    def retorna_geometria_semiarido(self) -> gpd.GeoSeries:
        query = "SELECT * FROM geoft.semiarido_2024"
        gdf = gpd.read_postgis(query, self.engine, geom_col="geom")
        return gdf.geometry

    def retorna_objetivos_rhnr(self, codigo_estacao: int) -> list[str]:
        with Session(self.engine) as session:
            query = select(EstacaoComObjetivos).where(
                EstacaoComObjetivos.codigo_estacao == codigo_estacao
            )
            response = session.execute(query).scalars().all()

        if not response:
            raise ValueError(
                f"Estação com código {codigo_estacao} não possui objetivos na RHNR."
            )
        return [obj.criterio for obj in response]
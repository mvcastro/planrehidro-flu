import os
from typing import Literal, Sequence

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, or_, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from planrehidro_flu.core.models import CurvaDeDescarga, EstacaoHidro, ResumoDeDescarga
from planrehidro_flu.databases.hidro.enums import (
    BaciaEnum,
    NivelConsistencia,
    ResponsavelEnum,
    TipoEstacao,
)
from planrehidro_flu.databases.hidro.models import (
    Bacia,
    CurvaDescarga,
    Entidade,
    Estacao,
    Estado,
    Municipio,
    PivotChuva,
    PivotCota,
    PivotVazao,
    ResumoDescarga,
    Rio,
    SubBacia,
)

load_dotenv()


class HidroDWReader:
    def __init__(self) -> None:
        driver = os.getenv("SQL_SERVER_DB_DRIVER")
        server = os.getenv("SQL_SERVERDB_SERVER")
        db_name = os.getenv("SQL_SERVER_DB_NAME")
        connection_string = f"Driver={driver};Server={server};Database={db_name};Trusted_Connection=yes;"
        connection_url = URL.create(
            "mssql+pyodbc", query={"odbc_connect": connection_string}
        )
        self.engine = create_engine(connection_url, use_setinputsizes=False)

    def retorna_inventario(self) -> list[Estacao]:
        with Session(self.engine) as session:
            query = session.query(Estacao)
            return query.all()

    def retorna_estacoes_por_codigo(self, codigos: Sequence[int]) -> Sequence[Estacao]:
        with Session(self.engine) as session:
            response = (
                session.execute(select(Estacao).where(Estacao.Codigo.in_(codigos)))
                .scalars()
                .all()
            )
            return response

    def retorna_inventario_por_bacia(
        self, bacia: BaciaEnum, tipo_estacao: TipoEstacao, operando: Literal[0, 1]
    ) -> Sequence[Estacao]:
        with Session(self.engine) as session:
            query = select(Estacao).where(
                Estacao.BaciaCodigo == bacia,
                Estacao.TipoEstacao == tipo_estacao,
                Estacao.Operando == operando,
            )
            return session.scalars(query).all()

    def retorna_serie_de_pivotchuva(
        self, codigo_estacao: int, nivel_consistencia: NivelConsistencia
    ) -> pd.DataFrame:
        query = (
            select(
                PivotChuva.EstacaoCodigo,
                PivotChuva.Data,
                PivotChuva.Chuva,
                PivotChuva.NivelConsistencia,
            )
            .where(
                PivotChuva.EstacaoCodigo == codigo_estacao,
                PivotChuva.NivelConsistencia == nivel_consistencia,
            )
            .order_by(PivotChuva.Data)
        )

        return pd.read_sql(query, self.engine, index_col="Data")

    def cria_inventario_estacao_hidro(self) -> list[EstacaoHidro]:
        with Session(self.engine) as session:
            stmt = (
                select(
                    Estacao.Codigo,
                    Estacao.Nome,
                    Estacao.Latitude,
                    Estacao.Longitude,
                    Estacao.Altitude,
                    Estacao.AreaDrenagem,
                    Bacia.Nome.label("Bacia"),
                    SubBacia.Nome.label("SubBacia"),
                    Rio.Nome.label("Rio"),
                    Estado.Nome.label("Estado"),
                    Municipio.Nome.label("Municipio"),
                    Entidade.Sigla.label("Responsavel"),
                    Estacao.TipoEstacao,
                    Estacao.TipoEstacaoTelemetrica,
                    Estacao.Operando,
                )
                .join(Bacia, Estacao.BaciaCodigo == Bacia.Codigo, isouter=True)
                .join(SubBacia, Estacao.SubBaciaCodigo == SubBacia.Codigo, isouter=True)
                .join(Estado, Estacao.EstadoCodigo == Estado.Codigo, isouter=True)
                .join(
                    Municipio, Estacao.MunicipioCodigo == Municipio.Codigo, isouter=True
                )
                .join(
                    Entidade, Estacao.ResponsavelCodigo == Entidade.Codigo, isouter=True
                )
                .join(Rio, Estacao.RioCodigo == Rio.Codigo, isouter=True)
                .where(
                    Estacao.Importado == 0,
                    Estacao.Temporario == 0,
                    Estacao.Removido == 0,
                    Estacao.ImportadoRepetido == 0,
                    Bacia.Importado == 0,
                    Bacia.Temporario == 0,
                    Bacia.Removido == 0,
                    Bacia.ImportadoRepetido == 0,
                    SubBacia.Importado == 0,
                    SubBacia.Temporario == 0,
                    SubBacia.Removido == 0,
                    SubBacia.ImportadoRepetido == 0,
                    Rio.Importado == 0,
                    Rio.Temporario == 0,
                    Rio.Removido == 0,
                    Rio.ImportadoRepetido == 0,
                    Estado.Importado == 0,
                    Estado.Temporario == 0,
                    Estado.Removido == 0,
                    Estado.ImportadoRepetido == 0,
                    Municipio.Importado == 0,
                    Municipio.Temporario == 0,
                    Municipio.Removido == 0,
                    Municipio.ImportadoRepetido == 0,
                    Estacao.TipoEstacao == TipoEstacao.FLUVIOMETRICA,
                    Estacao.ResponsavelCodigo == ResponsavelEnum.ANA,
                    Estacao.Operando == 1,
                    or_(
                        Estacao.Descricao.not_like("%%HIDROOBSERVA%%"),
                        Estacao.Descricao.is_(None),
                    ),
                ).union_all(
                    select(
                        Estacao.Codigo,
                        Estacao.Nome,
                        Estacao.Latitude,
                        Estacao.Longitude,
                        Estacao.Altitude,
                        Estacao.AreaDrenagem,
                        Bacia.Nome.label("Bacia"),
                        SubBacia.Nome.label("SubBacia"),
                        Rio.Nome.label("Rio"),
                        Estado.Nome.label("Estado"),
                        Municipio.Nome.label("Municipio"),
                        Entidade.Sigla.label("Responsavel"),
                        Estacao.TipoEstacao,
                        Estacao.TipoEstacaoTelemetrica,
                        Estacao.Operando,
                    )
                    .join(Bacia, Estacao.BaciaCodigo == Bacia.Codigo, isouter=True)
                    .join(
                        SubBacia,
                        Estacao.SubBaciaCodigo == SubBacia.Codigo,
                        isouter=True,
                    )
                    .join(Estado, Estacao.EstadoCodigo == Estado.Codigo, isouter=True)
                    .join(
                        Municipio,
                        Estacao.MunicipioCodigo == Municipio.Codigo,
                        isouter=True,
                    )
                    .join(
                        Entidade,
                        Estacao.ResponsavelCodigo == Entidade.Codigo,
                        isouter=True,
                    )
                    .join(Rio, Estacao.RioCodigo == Rio.Codigo, isouter=True)
                    .where(
                        Estacao.Importado == 0,
                        Estacao.Temporario == 0,
                        Estacao.Removido == 0,
                        Estacao.ImportadoRepetido == 0,
                        Estacao.TipoEstacao == TipoEstacao.FLUVIOMETRICA,
                        Estacao.ResponsavelCodigo == ResponsavelEnum.ANA,
                        Estacao.Operando == 1,
                        Estacao.OperadoraCodigo == ResponsavelEnum.SGB_CPRM,
                        Estacao.Descricao.like("%%HIDROOBSERVA%%"),
                    )
                )
            ).cte()

            resposta = session.execute(select(stmt).distinct().order_by(stmt.c.Codigo))
            rows_dict = [row._asdict() for row in resposta]
            lista_estacoes_hidro = [
                EstacaoHidro(
                    codigo=row_dict["Codigo"],
                    nome=row_dict["Nome"],
                    latitude=row_dict["Latitude"],
                    longitude=row_dict["Longitude"],
                    altitude=row_dict["Altitude"],
                    area_drenagem_km2=row_dict["AreaDrenagem"],
                    bacia=row_dict["Bacia"],
                    subbacia=row_dict["SubBacia"],
                    rio=row_dict["Rio"],
                    estado=row_dict["Estado"],
                    municipio=row_dict["Municipio"],
                    responsavel=row_dict["Responsavel"],
                    tipo_estacao=row_dict["TipoEstacao"],
                    estacao_telemetrica=row_dict["TipoEstacaoTelemetrica"],
                    operando=row_dict["Operando"],
                )
                for row_dict in rows_dict
            ]
            return lista_estacoes_hidro

    def retorna_resumo_de_descarga(self, codigo: int) -> list[ResumoDeDescarga]:
        query = (
            select(
                ResumoDescarga.EstacaoCodigo.label("codigo"),
                ResumoDescarga.NivelConsistencia.label("nivel_consistencia"),
                ResumoDescarga.Data.label("data"),
                ResumoDescarga.Cota.label("cota"),
                ResumoDescarga.Vazao.label("vazao"),
                ResumoDescarga.AreaMolhada.label("area_molhada"),
                ResumoDescarga.Largura.label("largura"),
                ResumoDescarga.VelMedia.label("vel_media"),
                ResumoDescarga.Profundidade.label("profundidade"),
            )
            .where(
                ResumoDescarga.EstacaoCodigo == codigo,
                ResumoDescarga.NivelConsistencia == 2,
                ResumoDescarga.Importado == 0,
                ResumoDescarga.Temporario == 0,
                ResumoDescarga.Removido == 0,
                ResumoDescarga.ImportadoRepetido == 0,
            )
            .order_by(ResumoDescarga.Data)
        )

        with Session(self.engine) as session:
            response = session.execute(query).all()
            result = [ResumoDeDescarga(**row._mapping) for row in response]
        return result

    def retorna_curva_de_descarga(self, codigo: int) -> list[CurvaDeDescarga]:
        query = (
            select(
                CurvaDescarga.EstacaoCodigo.label("codigo"),
                CurvaDescarga.NivelConsistencia.label("nivel_consistencia"),
                CurvaDescarga.PeriodoValidadeInicio.label("data_validade_inicio"),
                CurvaDescarga.PeriodoValidadeFim.label("data_validade_fim"),
                CurvaDescarga.CotaMaxima.label("cota_maxima"),
                CurvaDescarga.CotaMinima.label("cota_minima"),
                CurvaDescarga.TipoCurva.label("tipo_curva"),
                CurvaDescarga.TipoEquacao.label("tipo_equacao"),
                CurvaDescarga.CoefA.label("coef_a"),
                CurvaDescarga.CoefH0.label("coef_h0"),
                CurvaDescarga.CoefN.label("coef_n"),
                CurvaDescarga.CoefA0.label("coef_a0"),
                CurvaDescarga.CoefA1.label("coef_a1"),
                CurvaDescarga.CoefA2.label("coef_a2"),
                CurvaDescarga.CoefA3.label("coef_a3"),
            )
            .where(
                CurvaDescarga.EstacaoCodigo == codigo,
                CurvaDescarga.NivelConsistencia == 2,
                CurvaDescarga.Importado == 0,
                CurvaDescarga.Temporario == 0,
                CurvaDescarga.Removido == 0,
                CurvaDescarga.ImportadoRepetido == 0,
            )
            .order_by(CurvaDescarga.PeriodoValidadeInicio)
        )

        with Session(self.engine) as session:
            response = session.execute(query).all()
            result = [CurvaDeDescarga(**row._mapping) for row in response]
        return result

    def retorna_serie_historica_vazao(self, codigo: int) -> Sequence[PivotVazao]:
        query = select(PivotVazao).where(PivotVazao.EstacaoCodigo == codigo)
        with Session(self.engine) as session:
            response = session.scalars(query).all()
        return response

    def retorna_serie_historica_cota(
        self,
        codigo: int,
        nivel_consistencia: NivelConsistencia = NivelConsistencia.CONSISTIDO,
    ) -> Sequence[PivotCota]:
        query = select(PivotCota).where(
            PivotCota.EstacaoCodigo == codigo,
            PivotCota.NivelConsistencia == nivel_consistencia.value,
        )
        with Session(self.engine) as session:
            response = session.execute(query).scalars().all()
        return response

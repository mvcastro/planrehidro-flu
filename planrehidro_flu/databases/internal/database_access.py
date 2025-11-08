from typing import Sequence

from sqlalchemy import Engine, select, update
from sqlalchemy.orm import Session

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.parametros_multicriterio import NomeCampo
from planrehidro_flu.databases.internal.models import (
    CriteriosDaEstacao,
    EstacaoFluPorRH,
    InventarioEstacaoFluAna,
    RegiaoHidrografica,
)


def retorna_inventario(engine: Engine) -> Sequence[InventarioEstacaoFluAna]:
    """Insert a list of EstacaoHidro into the database."""
    with Session(engine) as session:
        response = session.execute(select(InventarioEstacaoFluAna)).scalars().all()
        return response


def retorna_estacoes_por_rh(engine: Engine) -> list[dict]:
    """Insert a list of EstacaoHidro into the database."""
    with Session(engine) as session:
        stmt = select(
            EstacaoFluPorRH.codigo, RegiaoHidrografica.rhi_nm.label("nome_rh")
        )
        print(stmt)
        response = session.execute(stmt)
        return [{"codigo": row[0], "nome_rh": row[1]} for row in response]


def retorna_estacoes_processadas(engine: Engine) -> list[int]:
    with Session(engine) as session:
        query = select(CriteriosDaEstacao).order_by(CriteriosDaEstacao.codigo_estacao)
        response = session.execute(query).scalars().all()
        return [estacao.codigo_estacao for estacao in response]


def retorna_criterios_das_estacoes(engine: Engine) -> Sequence[CriteriosDaEstacao]:
    with Session(engine) as session:
        response = session.execute(select(CriteriosDaEstacao)).scalars().all()
        return response


def retorna_criterios_por_rh(engine: Engine) -> Sequence[dict]:
    with Session(engine) as session:
        stmt = select(
            CriteriosDaEstacao.codigo_estacao,
            InventarioEstacaoFluAna.nome,
            InventarioEstacaoFluAna.latitude,
            InventarioEstacaoFluAna.longitude,
            CriteriosDaEstacao.area_dren,
            CriteriosDaEstacao.espacial,
            CriteriosDaEstacao.cheias,
            CriteriosDaEstacao.ish,
            CriteriosDaEstacao.semiarido,
            CriteriosDaEstacao.irrigacao,
            CriteriosDaEstacao.navegacao,
            CriteriosDaEstacao.extensao,
            CriteriosDaEstacao.desv_cchave,
            CriteriosDaEstacao.med_desc,
            CriteriosDaEstacao.est_energia,
            CriteriosDaEstacao.rhnr_c1,
            CriteriosDaEstacao.rhnr_c2,
            RegiaoHidrografica.rhi_nm.label("nome_rh"),
        ).where(
            CriteriosDaEstacao.codigo_estacao == EstacaoFluPorRH.codigo,
            EstacaoFluPorRH.rhi_cd == RegiaoHidrografica.rhi_cd,
            CriteriosDaEstacao.codigo_estacao == InventarioEstacaoFluAna.codigo,
        )
        response = session.execute(stmt).all()
        return [dict(row._mapping) for row in response]


def insere_inventario(engine: Engine, inventario: list[EstacaoHidro]) -> None:
    """Insert a list of EstacaoHidro into the database."""
    with Session(engine) as session:
        inventario_flu_ana = [
            InventarioEstacaoFluAna(**estacao.model_dump()) for estacao in inventario
        ]
        session.add_all(inventario_flu_ana)
        session.commit()


def insere_criterios_da_estacao(
    engine: Engine, valores_criterios: CriteriosDaEstacao
) -> None:
    with Session(engine) as session:
        session.add(valores_criterios)
        session.commit()


def update_criterio_da_estacao(
    engine: Engine,
    codigo_estacao: int,
    campo: NomeCampo,
    valor: int | float | bool | str | None,
) -> None:
    with Session(engine) as session:
        session.execute(
            update(CriteriosDaEstacao)
            .where(CriteriosDaEstacao.codigo_estacao == codigo_estacao)
            .values(**{campo: valor})  # type: ignore
        )
        session.commit()
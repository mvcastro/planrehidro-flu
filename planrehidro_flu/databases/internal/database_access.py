from typing import Sequence
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.databases.internal.models import (
    CriteriosDaEstacao,
    InventarioEstacaoFluAna,
)


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


def retorna_estacoes_processadas(engine: Engine) -> list[int]:
    with Session(engine) as session:
        query = select(CriteriosDaEstacao).order_by(
            CriteriosDaEstacao.codigo_estacao
        )
        response = session.execute(query).scalars().all()
        return [estacao.codigo_estacao for estacao in response]
    
def retorna_criterios_das_estacoes(engine: Engine) -> Sequence[CriteriosDaEstacao]:
    with Session(engine) as session:
        response = session.execute(select(CriteriosDaEstacao)).scalars().all()
        return response
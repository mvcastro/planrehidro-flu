from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.parametros_multicriterio import CriterioSelecionado
from planrehidro_flu.databases.internal.models import (
    Criterio,
    GrupoCriterios,
    InventarioEstacoesFluAna,
    ValorCriterio,
)


def insere_inventario(engine: Engine, inventario: list[EstacaoHidro]) -> None:
    """Insert a list of EstacaoHidro into the database."""
    with Session(engine) as session:
        inventario_flu_ana = [
            InventarioEstacoesFluAna(**estacao.model_dump()) for estacao in inventario
        ]
        session.add_all(inventario_flu_ana)
        session.commit()


def insere_criterio(
    engine: Engine,
    codigo_estacao: int,
    criterio_selecionado: CriterioSelecionado,
    valor_criterio: float | str | bool,
) -> None:
    with Session(engine) as session:
        grupo_obj = GrupoCriterios(grupo=criterio_selecionado["grupo"])
        grupo_cadastrado = session.execute(
            select(GrupoCriterios).where(GrupoCriterios.grupo == grupo_obj.grupo)
        ).scalar()
        
        if not grupo_cadastrado:
            session.add(grupo_obj)
            session.commit()
            session.refresh(grupo_obj)
        else:
            grupo_obj = grupo_cadastrado
        
        criterio_obj = Criterio(
            grupo_id=grupo_obj.id,
            criterio=criterio_selecionado["criterio"],
            unidade=criterio_selecionado["unidade"], 
        )
        
        criterio_cadastrado = session.execute(
            select(Criterio).where(Criterio.criterio == criterio_obj.criterio)
        ).scalar()
            
        if not criterio_cadastrado:
            session.add(criterio_obj)
            session.commit()
            session.refresh(criterio_obj)
        else:
            criterio_obj = criterio_cadastrado
        
        valor_criterio_obj = ValorCriterio(
            codigo_estacao=codigo_estacao,
            criterio=criterio_obj,
            valor=valor_criterio,
        )
        session.add(valor_criterio_obj)
        session.commit()

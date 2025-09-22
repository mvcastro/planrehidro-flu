from typing import Sequence

import pandas as pd
import streamlit as st

from planrehidro_flu.core.parametros_multicriterio import parametros_multicriterio
from planrehidro_flu.databases.internal.database_access import (
    retorna_criterios_das_estacoes,
    retorna_criterios_por_rh,
    retorna_estacoes_por_rh,
    retorna_inventario,
)
from planrehidro_flu.databases.internal.models import ENGINE, InventarioEstacaoFluAna


@st.cache_resource
def get_engine():
    return ENGINE


@st.cache_data
def get_dados_criterios(_engine) -> pd.DataFrame:
    criterios = retorna_criterios_das_estacoes(_engine)
    return pd.DataFrame([criterio.to_dict() for criterio in criterios])


@st.cache_data
def get_estacoes_por_rh(_engine) -> pd.DataFrame:
    estacoes_por_rh = retorna_estacoes_por_rh(_engine)
    return pd.DataFrame(estacoes_por_rh)


@st.cache_data
def get_dados_criterios_por_rh(_engine) -> pd.DataFrame:
    criterios_por_rh = retorna_criterios_por_rh(_engine)
    return pd.DataFrame(criterios_por_rh)


@st.cache_data
def get_inventario(_engine) -> Sequence[InventarioEstacaoFluAna]:
    inventario_estacoes = retorna_inventario(_engine)
    return inventario_estacoes


@st.cache_data
def get_data_dictionary() -> pd.DataFrame:
    parametros = []
    for params in parametros_multicriterio:
        parametros.append(
            {key: value for key, value in params.items() if key != "calculo"}
        )
    return pd.DataFrame(parametros).sort_values("grupo")


engine = get_engine()
df_criterios_rh = get_dados_criterios_por_rh(engine)
df_dicionario = get_data_dictionary()
inventario_estacoes = get_inventario(engine)
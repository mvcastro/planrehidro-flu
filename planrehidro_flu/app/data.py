from typing import Sequence

import pandas as pd
import streamlit as st

from planrehidro_flu.core.parametros_multicriterio import parametros_multicriterio
from planrehidro_flu.databases.cplar.bd_cplar_reader import PostgresReader
from planrehidro_flu.databases.internal.database_access import (
    retorna_criterios_das_estacoes,
    retorna_criterios_por_rh,
    retorna_estacoes_por_rh,
    retorna_inventario,
)
from planrehidro_flu.databases.internal.models import (
    ENGINE,
    InventarioEstacaoFluAna,
)


@st.cache_resource
def get_engine():
    return ENGINE


@st.cache_data
def get_dados_criterios(_engine) -> list[dict]:
    criterios = retorna_criterios_das_estacoes(_engine)
    dict_criterios = [criterio.to_dict() for criterio in criterios]
    # Formatando dados do Critéio ish ->
    # Mínimo e Baixo = 1 / Médio, Alto e Máximo = 0
    formatacao_ish = {
        "Mínimo": 1,
        "Baixo": 1,
        "Médio": 0,
        "Alto": 0,
        "Máximo": 0,
    }
    for criterio in dict_criterios:
        criterio["ish"] = formatacao_ish[criterio["ish"]]
    return dict_criterios


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


@st.cache_data
def get_retorna_estacoes_rhnr_cenario1() -> pd.DataFrame:
    cplar_reader = PostgresReader()
    estacoes_c1 = cplar_reader.retorna_estacoes_rhnr_cenario1()
    return pd.DataFrame([estacao.to_dict() for estacao in estacoes_c1])

@st.cache_data
def get_retorna_estacoes_rhnr_cenario2() -> pd.DataFrame:
    cplar_reader = PostgresReader()
    estacoes_c2 = cplar_reader.retorna_estacoes_rhnr_cenario2()
    return pd.DataFrame([estacao.to_dict() for estacao in estacoes_c2])


engine = get_engine()
df_criterios_rh = get_dados_criterios_por_rh(engine)
df_dicionario = get_data_dictionary()
dados_criterios_estacoes = get_dados_criterios(engine)

from typing import get_args

import streamlit as st

from planrehidro_flu.app.data import df_criterios_rh, df_dicionario
from planrehidro_flu.core.parametros_multicriterio import NomeCampo

st.subheader("Dicionário de Dados dos Critérios na tabela")
st.dataframe(df_dicionario, hide_index=True)

st.subheader("Estatística dos dados dos Critérios Numéricos")
st.dataframe(df_criterios_rh[list(get_args(NomeCampo))[1:]].describe().T)

st.subheader("Valores Resultantes dos Critérios")
option = st.selectbox(
    "Código da Estação Fluviométrica:",
    options=df_criterios_rh["codigo_estacao"],
    index=None,
    placeholder="Selecione um código de estação para filtar a tabela...",
)
COLUNAS = [
    "codigo_estacao",
    "nome",
    "area_dren",
    "espacial",
    "ish",
    "irrigacao",
    "navegacao",
    "extensao",
    "desv_cchave",
    "med_desc",
    "est_energia",
    "rhnr_c1",
]

if option:
    st.dataframe(
        df_criterios_rh[COLUNAS][df_criterios_rh.codigo_estacao == option],
        hide_index=True,
    )
else:
    st.dataframe(df_criterios_rh[COLUNAS], hide_index=True)

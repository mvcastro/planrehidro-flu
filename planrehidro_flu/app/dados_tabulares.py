import streamlit as st

from planrehidro_flu.app.data import df_criterios_rh, df_dicionario

st.text("Dicionário de Dados dos Critérios na tabela")
st.dataframe(df_dicionario, hide_index=True)


st.text("Valores Resultantes dos Critérios")
st.dataframe(df_criterios_rh, hide_index=True)

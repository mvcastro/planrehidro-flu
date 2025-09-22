from typing import TypedDict

import streamlit as st

from planrehidro_flu.app.pages import get_page_function
from planrehidro_flu.core.parametros_multicriterio import NomeCampo

st.set_page_config(page_title="PlanReHidro", page_icon="💧", layout="wide")


class PageData(TypedDict):
    campo: NomeCampo
    title: str
    icon: str


pages: list[PageData] = [
    {
        "campo": "area_dren",
        "title": "Área Drenagem",
        "icon": ":material/finance:",
    },
    {
        "campo": "espacial",
        "title": "Relevância Espacial",
        "icon": ":material/finance:",
    },
    {
        "campo": "extensao",
        "title": "Extensão da Série",
        "icon": ":material/finance:",
    },
    {
        "campo": "desv_cchave",
        "title": "Desvio Curva-Chave",
        "icon": ":material/finance:",
    },
    {
        "campo": "med_desc",
        "title": "Descargas médias anuais",
        "icon": ":material/finance:",
    },
    #                             {
    #     "campo": "espacial",
    #     "title": "Relevância Espacial",
    #     "icon": ":material/finance:",
    # },
]


pg = st.navigation(
    {
        "Mapa": [st.Page("mapa.py", title="Estações Fluviométricas", icon="📍")],
        "Dados": [
            st.Page(
                "dados_tabulares.py",
                title="Tabela de Dados",
                icon=":material/data_table:",
            )
        ],
        "Critérios:": [
            st.Page(
                get_page_function(page["campo"]), title=page["title"], icon=page["icon"]
            )
            for page in pages
        ],
    }
)
pg.run()

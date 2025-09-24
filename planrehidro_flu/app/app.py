from typing import TypedDict

import streamlit as st

from planrehidro_flu.app.pages import default_categorical_page, default_numerical_page, get_page_function
from planrehidro_flu.core.parametros_multicriterio import NomeCampo

st.set_page_config(page_title="PlanReHidro", page_icon="💧", layout="wide")


class PageData(TypedDict):
    campo: NomeCampo
    title: str
    icon: str


categorical_pages: list[PageData] = [
    {
        "campo": "est_energia",
        "title": "Próximo à estação do Setor Elétrico",
        "icon": ":material/finance:",
    },
    {
        "campo": "cheias",
        "title": "Em Trecho Vulnerável a cheias",
        "icon": ":material/finance:",
    },
    {
        "campo": "ish",
        "title": "ISH na Área de Drenagem",
        "icon": ":material/finance:",
    },
    {
        "campo": "irrigacao",
        "title": "Em Polos Nacionais de Irrigação",
        "icon": ":material/finance:",
    },
    {
        "campo": "navegacao",
        "title": "Em Trecho para Navegação",
        "icon": ":material/finance:",
    },
]


numerical_pages: list[PageData] = [
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
        "Critérios Categóricos:": [
            st.Page(
                get_page_function(page["campo"], default_categorical_page), title=page["title"], icon=page["icon"]
            )
            for page in categorical_pages
        ],
        "Critérios Numéricos:": [
            st.Page(
                get_page_function(page["campo"], default_numerical_page),
                title=page["title"],
                icon=page["icon"],
            )
            for page in numerical_pages
        ],
    }
)
pg.run()

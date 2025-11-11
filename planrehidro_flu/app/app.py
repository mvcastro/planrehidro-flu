from pathlib import Path
from typing import TypedDict

import streamlit as st

from planrehidro_flu.app.paginas.config_pesos_params import (
    default_page_config_params_points,
    default_page_config_params_weights,
    gera_resultados,
)
from planrehidro_flu.app.paginas.default_pages import (
    default_page_stats_categorical_params,
    default_page_stats_numerical_params,
    get_page_function,
)
from planrehidro_flu.core.parametros_multicriterio import NomeCampo

st.set_page_config(page_title="PlanReHidro", page_icon="💧", layout="wide")


FOLDER_PAGES = Path("paginas")


class PageData(TypedDict):
    campo: NomeCampo
    title: str
    icon: str


categorical_pages: list[PageData] = [
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
        "campo": "est_energia",
        "title": "Próximo à estação do Setor Elétrico",
        "icon": ":material/finance:",
    },
    {
        "campo": "rhnr_c1",
        "title": "Proximidade à estação da RHNR - Cenário 1",
        "icon": ":material/finance:",
    },
    {
        "campo": "rhnr_c2",
        "title": "Proximidade à estação da RHNR - Cenário 2",
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
        # "Mapa": [
        #     st.Page(
        #         FOLDER_PAGES / "mapa.py", title="Estações Fluviométricas", icon="📍"
        #     )
        # ],
        "Dados": [
            st.Page(
                FOLDER_PAGES / "dados_tabulares.py",
                title="Tabela de Dados",
                icon=":material/data_table:",
            )
        ],
        "Estatísticas dos Critérios Categóricos:": [
            st.Page(
                get_page_function(
                    nome_campo=page["campo"],
                    page_function=default_page_stats_categorical_params,
                    page_type="stats",
                ),
                title=page["title"],
                icon=":material/finance:",
            )
            for page in categorical_pages
        ],
        "Estatísticas dos Critérios Numéricos:": [
            st.Page(
                get_page_function(
                    nome_campo=page["campo"],
                    page_function=default_page_stats_numerical_params,
                    page_type="stats",
                ),
                title=page["title"],
                icon=page["icon"],
            )
            for page in numerical_pages
        ],
        "Processamento dos Pesos e Critérios": [
            st.Page(
                default_page_config_params_weights,
                title="Pesos",
                icon=":material/settings:",
            ),
            st.Page(
                default_page_config_params_points,
                title="Critérios",
                icon=":material/settings:",
            ),
            st.Page(gera_resultados, title="Resultados", icon=":material/rubric:"),
        ],
    }
)
pg.run()

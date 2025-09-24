from typing import Callable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from planrehidro_flu.app.data import df_criterios_rh
from planrehidro_flu.core.parametros_multicriterio import (
    CriterioSelecionado,
    NomeCampo,
    parametros_multicriterio,
)


def search_criterio_props(nome_campo: NomeCampo) -> CriterioSelecionado:
    for criterio in parametros_multicriterio:
        if criterio["nome_campo"] == nome_campo:
            return criterio
    raise ValueError(f"Critério {nome_campo} não encontrado.")


def cdf(data: np.ndarray | pd.Series) -> tuple[np.ndarray, np.ndarray]:
    x = np.sort(data)
    n = x.size
    y = np.arange(1, n + 1) / n
    return x, y


DefaultPageFunction = Callable[[NomeCampo], None]


def default_categorical_page(nome_campo: NomeCampo) -> None:
    criterio = search_criterio_props(nome_campo)
    criterio_str = f"{criterio['descricao']} [{criterio['unidade']}]"

    labels = df_criterios_rh[nome_campo].unique()
    values = df_criterios_rh[nome_campo].value_counts()

    st.title("Resultados Globais")
    st.subheader(f"Critério: {criterio_str}")

    tab1, tab2 = st.tabs(
        ["Dados de todas as estações", "Dados por Região Hidrográfica"]
    )

    with tab1:
        st.plotly_chart(
            go.Figure(
                data=go.Pie(labels=labels, values=values, hole=0.3),
                layout=go.Layout(title=go.layout.Title(text="Gráfico de Pizza")),
            )
        )

    with tab2:
        rh_names = df_criterios_rh["nome_rh"].unique()
        
        fig = make_subplots(
            rows=4,
            cols=3,
            specs=[
                [{"type": "domain"}, {"type": "domain"}, {"type": "domain"}],
                [{"type": "domain"}, {"type": "domain"}, {"type": "domain"}],
                [{"type": "domain"}, {"type": "domain"}, {"type": "domain"}],
                [{"type": "domain"}, {"type": "domain"}, {"type": "domain"}],
            ],
            subplot_titles=rh_names,
        )

        n_subplot = 1
        row = 1
        for idx, nome_rh in enumerate(rh_names):
            data = df_criterios_rh[df_criterios_rh["nome_rh"] == nome_rh]
            
            labels_rh = data[nome_campo].unique()
            values_rh = data[nome_campo].value_counts()

            col = n_subplot % 3 if n_subplot % 3 != 0 else 3
            fig.add_trace(
                go.Pie(labels=labels_rh, values=values_rh, name=nome_rh, hole=0.4),
                row=row,
                col=col,
            )
            row = row + 1 if n_subplot % 3 == 0 else row
            n_subplot += 1

        fig.update_layout(
            height=800,
            title="Gráfico de Pizza por Região Hidrográfica",)
        st.plotly_chart(fig)


def default_numerical_page(nome_campo: NomeCampo) -> None:
    criterio = search_criterio_props(nome_campo)
    criterio_str = f"{criterio['descricao']} [{criterio['unidade']}]"

    x_data = df_criterios_rh[nome_campo]
    x_cdf, y_cdf = cdf(x_data)

    st.title("Resultados Globais")
    st.subheader(f"Critério: {criterio_str}")

    tab1, tab2 = st.tabs(
        ["Dados de todas as estações", "Dados por Região Hidrográfica"]
    )

    with tab1:
        st.plotly_chart(
            go.Figure(
                data=go.Histogram(x=x_data),
                layout=go.Layout(title=go.layout.Title(text="Histograma")),
            ).update_layout(
                xaxis=dict(title=criterio_str), yaxis=dict(title="Frequência")
            )
        )

        st.plotly_chart(
            go.Figure(
                data=go.Box(x=x_data, name=nome_campo),
                layout=go.Layout(title=go.layout.Title(text="Box-Plot")),
            ).update_layout(xaxis=dict(title=criterio_str))
        )

        st.plotly_chart(
            go.Figure(
                data=go.Scatter(x=x_cdf, y=y_cdf, name=nome_campo),
                layout=go.Layout(title=go.layout.Title(text="Curva de Permanência")),
            ).update_layout(
                xaxis=dict(title=criterio_str), yaxis=dict(title="Permanência")
            )
        )

    with tab2:
        # Box-plots
        fig = make_subplots(rows=4, cols=3)
        # Cruvas de permanência
        fig2 = make_subplots(
            rows=4,
            cols=3,
            horizontal_spacing=0.1,  # Adjust horizontal space
            vertical_spacing=0.2,
        )

        n_subplot = 1
        row = 1
        for nome_rh, data in df_criterios_rh[["nome_rh", nome_campo]].groupby(
            "nome_rh"
        ):
            x_cdf_rh, y_cdf_rh = cdf(data[nome_campo])

            col = n_subplot % 3 if n_subplot % 3 != 0 else 3
            fig.add_trace(go.Box(y=data[nome_campo], name=nome_rh), row=row, col=col)

            fig2.add_trace(
                go.Scatter(x=x_cdf_rh, y=y_cdf_rh, name=nome_rh), row=row, col=col
            )
            fig2.update_xaxes(title_text=criterio["unidade"], row=row, col=col)
            fig2.update_yaxes(title_text="Permanência", row=row, col=col)

            row = row + 1 if n_subplot % 3 == 0 else row
            n_subplot += 1

        fig.update_layout(height=800, title="Box-Plot por Região Hidrográfica")
        fig2.update_layout(
            height=800, title="Curva de Permanência por Região Hidrográfica"
        )

        st.plotly_chart(fig)
        st.plotly_chart(fig2)


def get_page_function(nome_campo: NomeCampo, page_function: DefaultPageFunction):
    def funcao():
        return page_function(nome_campo=nome_campo)

    funcao.__name__ = nome_campo
    return funcao

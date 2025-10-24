from io import BytesIO
from typing import cast

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from planrehidro_flu.app.consistencia_dataframe import (
    checa_consistencia_dado_categorico,
    checa_consistencia_entre_as_classes,
    checa_consistencia_pontuacao,
    checa_consistencia_valores_da_classe,
)
from planrehidro_flu.app.pages import cdf
from planrehidro_flu.app.params_default_values import (
    DEFAULT_PARAMS_CLASSES,
    DEFAULT_WEIGTH_PARAMS,
)
from planrehidro_flu.app.processamento_multicriterio import (
    CriteriosProcessamento,
    processa_criterios,
)
from planrehidro_flu.core.parametros_multicriterio import (
    NomeCampo,
    parametros_multicriterio,
)


def checa_consistencia_params():
    for state in st.session_state:
        if state.startswith("params_"):
            idx_ini = state.find("_") + 1
            idx_fim = state.find("_default_df")
            nome_campo = state[idx_ini:idx_fim]
            df = st.session_state[state]
            if "Categoria" in df.columns:
                checa_consistencia_dado_categorico(df, nome_campo)
            else:
                checa_consistencia_valores_da_classe(df, nome_campo)
                checa_consistencia_entre_as_classes(df, nome_campo)
            checa_consistencia_pontuacao(df, nome_campo)


def gera_criterios_para_processamento(session_state: dict) -> CriteriosProcessamento:
    criterios_proc: CriteriosProcessamento = {}
    for state in st.session_state:
        if state.startswith("params_"):
            idx_ini = state.find("_") + 1
            idx_fim = state.find("_default_df")
            nome_campo = state[idx_ini:idx_fim]
            df = st.session_state[state]
            criterios_proc[nome_campo] = df
    return criterios_proc


def gera_graficos_dos_resultados(df_resultado: pd.DataFrame) -> None:
    st.plotly_chart(
        go.Figure(
            data=go.Histogram(x=df_resultado["Total"]),
            layout=go.Layout(
                title=go.layout.Title(text="Histograma da Pontuação Total das Estações")
            ),
        ).update_layout(
            xaxis=dict(title="Pontuação Total"), yaxis=dict(title="Frequência")
        )
    )

    x_cdf, y_cdf = cdf(df_resultado["Total"])
    st.plotly_chart(
        go.Figure(
            data=go.Scatter(
                x=x_cdf,
                y=y_cdf,
            ),
            layout=go.Layout(
                title=go.layout.Title(
                    text="Curva de Permanência da Pontuação Total das Estações"
                )
            ),
        ).update_layout(
            xaxis=dict(title="Pontuação Total"), yaxis=dict(title="Permanência")
        )
    )


def gera_resultados(df_resultado: None | pd.DataFrame = None):
    st.header("Resultados do Processamento")
    if "resultado" not in st.session_state:
        st.warning("Parâmetros não configurados!", icon="⚠️")
    else:
        df_resultado = st.session_state["resultado"]
        if df_resultado is None:
            st.warning("Parâmetros não configurados!", icon="⚠️")
        else:
            gera_graficos_dos_resultados(df_resultado)
            filtro = st.selectbox(
                label="Selecione a estação para ver o seu resultado:",
                options=df_resultado["codigo_estacao"],
                index=None,
            )
            if filtro:
                st.dataframe(df_resultado[df_resultado["codigo_estacao"] == filtro])
            else:
                st.dataframe(df_resultado)

                st.download_button(
                    label="Download da Tabela",
                    data=to_excel(df_resultado),
                    mime="application/vnd.ms-excel",
                    file_name="priorizacao_estacoes_flu_rhnr.xlsx",
                    type="primary",
                )


def to_excel(df):
    """
    Converts a Pandas DataFrame to an Excel file in-memory.
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    df.to_excel(writer, index=False)
    writer.close()  # Use writer.close() instead of writer.save() for newer pandas versions
    processed_data = output.getvalue()
    return processed_data


def get_default_dataframe(nome_campo: NomeCampo):
    if nome_campo not in DEFAULT_PARAMS_CLASSES:
        initial_df = pd.DataFrame(
            [
                {"Categoria": "Não", "Pontuação": 0},
                {"Categoria": "Sim", "Pontuação": 3},
            ]
        )
    else:
        initial_df = pd.DataFrame(
            [
                {
                    # "Ordem": key,
                    "Valor Inferior": values[0],
                    "Valor Superior": values[1],
                    "Pontuação": values[2],
                }
                for values in DEFAULT_PARAMS_CLASSES[nome_campo]
            ]
        )
    return initial_df


def reset_data_editor_state(nome_campo: NomeCampo):
    """Function to reset the DataFrame in session state."""
    st.session_state[f"params_{nome_campo}_default_df"] = get_default_dataframe(
        nome_campo
    )


def default_page_config_params_weights() -> None:
    st.subheader("Configuração dos valores dos Pesos")

    df_weigths = pd.DataFrame(
        [
            {
                "Critério": criterio["descricao"],
                "Peso": DEFAULT_WEIGTH_PARAMS[criterio["nome_campo"]],
            }
            for criterio in parametros_multicriterio
            if criterio["nome_campo"] in DEFAULT_WEIGTH_PARAMS
        ]
    )

    st.data_editor(df_weigths, num_rows="dynamic", width=600, key="weigths")


def default_page_config_params_points() -> None:
    st.subheader("Configuração da pontuação das classes dos Critérios")

    for criterio in parametros_multicriterio:
        criterio_str = f"{criterio['descricao']} [{criterio['unidade']}]"
        nome_campo = criterio["nome_campo"]

        st.text(criterio_str)

        editable_df = st.data_editor(
            get_default_dataframe(nome_campo),
            num_rows="dynamic",
            width=600,
            key=f"data_editor_{nome_campo}",
        )

        st.session_state[f"params_{nome_campo}_default_df"] = editable_df

    botao_restaurar_padrao = st.button(
        "Restaurar valores padrão", type="primary", icon="♻️"
    )
    if botao_restaurar_padrao:
        st.rerun()

    st.session_state["resultado"] = None
    processar = st.button("⚡ Processar ⚡")
    if processar:
        checa_consistencia_params()
        criterios_proc = gera_criterios_para_processamento(cast(dict, st.session_state))
        progress_bar = st.progress(0, text="Processando critérios...")
        df_resultado = processa_criterios(criterios_proc, progress_bar)
        st.session_state["resultado"] = df_resultado
        st.page_link(
            st.Page(gera_resultados, title="Resultados", icon=":material/rubric:")
        )

import pandas as pd
import streamlit as st

from planrehidro_flu.app.consistencia_dataframe import (
    checa_consistencia_dado_categorico,
    checa_consistencia_entre_as_classes,
    checa_consistencia_pontuacao,
    checa_consistencia_valores_da_classe,
)
from planrehidro_flu.app.params_default_values import (
    DEFAULT_PARAMS_CLASSES,
    DEFAULT_WEIGTH_PARAMS,
)
from planrehidro_flu.core.parametros_multicriterio import (
    NomeCampo,
    parametros_multicriterio,
)


def checa_consistencia_params():
    for state in st.session_state:
        if state.startswith("params_"):
            nome_campo = state.split("_")[1]
            df = st.session_state[state]
            if "Categoria" in df.columns:
                checa_consistencia_dado_categorico(df, nome_campo)
            else:
                checa_consistencia_valores_da_classe(df, nome_campo)
                checa_consistencia_entre_as_classes(df, nome_campo)
            checa_consistencia_pontuacao(df, nome_campo)


def gera_resultados():
    st.json(st.session_state)
    st.header("Resultados do Processamento")
    if "processado" not in st.session_state:
        st.warning("Parâmetros não configurados!", icon="⚠️")
    elif not st.session_state["processado"]:
        st.warning("Parâmetros não configurados!", icon="⚠️")
    else:
        st.subheader("Resultados...")
        checa_consistencia_params()


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

    st.session_state["processado"] = False
    processar = st.button("⚡ Processar ⚡")
    if processar:
        st.session_state["processado"] = True
        st.text("Processando...")
        st.page_link(
            st.Page(gera_resultados, title="Resultados", icon=":material/rubric:")
        )


def default_page_config_params_points_v2() -> None:
    st.subheader("Configuração da pontuação das classes dos Critérios")

    for criterio in parametros_multicriterio:
        criterio_str = f"{criterio['descricao']} [{criterio['unidade']}]"
        nome_campo = criterio["nome_campo"]

        col1, col2 = st.columns(2, vertical_alignment="bottom")
        with col1:
            st.text(criterio_str)

            # Initialize the DataFrame in session state
            if f"params_{nome_campo}_default_df" not in st.session_state:
                st.session_state[f"params_{nome_campo}_default_df"] = (
                    get_default_dataframe(nome_campo)
                )

            edited_df = st.data_editor(
                st.session_state[f"params_{nome_campo}_default_df"],
                num_rows="dynamic",
                width=600,
                key=f"data_editor_{nome_campo}",
            )

            # Update the session state DataFrame after edits
            st.session_state[f"params_{nome_campo}_default_df"] = edited_df

        with col2:
            botao_restaurar_padrao = st.button(
                "Restaurar valores padrão",
                type="primary",
                icon="♻️",
                key=f"botao_{nome_campo}",
            )
            if botao_restaurar_padrao:
                reset_data_editor_state(nome_campo=nome_campo)
                st.rerun()  # Rerun the app to display the reset data

    processar = st.button("Processar!")

    if processar:
        st.text("Processando...")


# def default_page_config_numerical_params() -> None:
#     criterio = search_criterio_props(nome_campo)
#     criterio_str = f"{criterio['descricao']} [{criterio['unidade']}]"

#     st.subheader("Configuração dos valores dos Pesos e Critérios")
#     st.text(criterio_str)

#     # Initialize the DataFrame in session state
#     if f"params_{nome_campo}_default_df" not in st.session_state:
#         # Create a sample DataFrame
#         initial_df = pd.DataFrame(
#             [
#                 {
#                     # "Ordem": key,
#                     "Valor Inferior": values[0],
#                     "Valor Superior": values[1],
#                     "Pontuação": values[2],
#                 }
#                 for _, values in DEFAULT_PARAMS_CLASSES[criterio["nome_campo"]].items()
#             ]
#         )
#         st.session_state[f"params_{nome_campo}_default_df"] = initial_df.copy()

#     if f"params_{nome_campo}_peso" not in st.session_state:
#         st.session_state[f"params_{nome_campo}_peso"] = 1

#     def reset_data_editor_state():
#         """Function to reset the DataFrame in session state."""
#         # Create a sample DataFrame
#         initial_df = pd.DataFrame(
#             [
#                 {
#                     # "Ordem": key,
#                     "Valor inf.": values[0],
#                     "Valor sup.": values[1],
#                     "Pontuação": values[2],
#                 }
#                 for _, values in DEFAULT_PARAMS_CLASSES[criterio["nome_campo"]].items()
#             ]
#         )
#         st.session_state[f"params_{nome_campo}_default_df"] = initial_df.copy()
#         st.session_state[f"params_{nome_campo}_peso"] = 1

#     edited_df = st.data_editor(
#         st.session_state[f"params_{nome_campo}_default_df"],
#         num_rows="dynamic",
#         width=600,
#     )

#     peso = st.number_input(
#         label="Defina o peso do critério:",
#         min_value=0,
#         max_value=10,
#         value=st.session_state[f"params_{nome_campo}_peso"],
#         step=1,
#         width=150,
#     )

#     # Update the session state DataFrame after edits
#     st.session_state[f"params_{nome_campo}_default_df"] = edited_df
#     st.session_state[f"params_{nome_campo}_peso"] = peso

#     botao_restaurar_padrao = st.button(
#         "Restaurar valores padrão", type="primary", icon="♻️"
#     )
#     if botao_restaurar_padrao:
#         reset_data_editor_state()
#         st.rerun()  # Rerun the app to display the reset data

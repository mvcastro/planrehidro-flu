import numpy as np
import pandas as pd


def checa_consistencia_dado_categorico(df: pd.DataFrame, nome_campo: str):
    for idx in df.index:
        categoria = df.loc[idx, "Categoria"]
        if df[df.index == categoria].shape[0] > 1:
            raise ValueError(f"Categoria repetida para o critério {nome_campo}!")

        if df["Categoria"].duplicated().any():
            raise ValueError(
                f"Os valores categóricos não estão consistentes para o critério {nome_campo}!"
            )


def checa_consistencia_pontuacao(df: pd.DataFrame, nome_campo: str):
    if df["Pontuação"].duplicated().any():
        raise ValueError(
            f"Valores de Pontuação repetidas para o critério {nome_campo}!"
        )


def checa_consistencia_valores_da_classe(df: pd.DataFrame, nome_campo: str):
    for _, row in df.iterrows():
        if row["Valor Inferior"] > row["Valor Superior"]:
            raise ValueError(
                "Valor Inferior maior que Valor Superior:"
                f"{row['Valor Inferior']} > {row['Valor Superior']}- {nome_campo}!"
            )

        if row["Valor Inferior"].isna():
            raise ValueError("Valor Inferior não pode ser nulo! - {nome_campo}")

        if row["Valor Inferior"].isna() and row["Valor Superior"].isna():
            raise ValueError(
                "Valor Inferior e Superior não podem ser nulos! - {nome_campo}"
            )


def checa_consistencia_entre_as_classes(df: pd.DataFrame, nome_campo: str):
    for idx, row_i in df.iterrows():
        valor_inf_i = row_i["Valor Inferior"]
        valor_sup_i = row_i["Valor Superior"]

        if np.isnan(valor_inf_i) and np.isnan(valor_sup_i) is None:
            continue

        if np.isnan(valor_sup_i):
            valor_sup_i = np.inf

        for _, row_j in df[df.index != idx].iterrows():
            valor_inf_j = row_j["Valor Inferior"]
            valor_sup_j = row_j["Valor Superior"]

            if np.isnan(valor_inf_j) and np.isnan(valor_sup_j):
                continue

            if np.isnan(valor_sup_j):
                valor_sup_j = np.inf

            if valor_inf_j > valor_inf_i and valor_inf_j < valor_sup_i:
                raise ValueError(f"Os intervaloes estão sobrepostos! - {nome_campo}")

            if valor_sup_j > valor_inf_i   and valor_sup_j < valor_sup_i:
                raise ValueError(f"Os intervaloes estão sobrepostos! - {nome_campo}")

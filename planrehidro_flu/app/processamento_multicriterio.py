from typing import get_args
import numpy as np
import pandas as pd

from planrehidro_flu.app.data import dados_criterios_estacoes
from planrehidro_flu.core.parametros_multicriterio import NomeCampo

type CriteriosProcessamento = dict[NomeCampo, pd.DataFrame]


def calculo_dados_categoricos(dataframe: pd.DataFrame, categoria: str) -> float:
    df = dataframe.copy()
    if categoria not in df["Categoria"].unique():
        raise ValueError(f"A categoria informada '{categoria}' não existe!")
    return df.loc[df["Categoria"] == categoria, "Pontuação"].values[0]


def calculo_dados_numericos(df: pd.DataFrame, valor_criterio: float) -> float:
    if df["Valor Superior"].hasnans:
        df.loc[df["Valor Superior"].isna(), "Valor Superior"] = np.inf

    return df.loc[
        (df["Valor Inferior"] <= valor_criterio)
        & (df["Valor Superior"] > valor_criterio),
        "Pontuação",
    ].values[0]


def processa_criterios(criterios_proc: CriteriosProcessamento, progress_bar) -> pd.DataFrame:
    total_estacoes = len(dados_criterios_estacoes)
    
    pontuacoes: list[dict[NomeCampo, float]] = []
    for idx, estacao in enumerate(dados_criterios_estacoes, start=1):
        pontuacao_estacao: dict[NomeCampo, float] = {}
        for nome_campo, df in criterios_proc.items():
            if "Categoria" in df.columns:
                categoricos = {0: "Não", 1: "Sim"}
                categoria = categoricos[estacao[nome_campo]]
                pontuacao = calculo_dados_categoricos(df, categoria)
            else:
                valor_criterio = estacao[nome_campo] if estacao[nome_campo] is not None else 0.0            
                valor_criterio = valor_criterio if valor_criterio >= 0.0 else 0.0
                pontuacao = calculo_dados_numericos(df, valor_criterio)
            pontuacao_estacao[nome_campo] = pontuacao
        pontuacao_estacao["codigo_estacao"] = estacao["codigo_estacao"]
        pontuacoes.append(pontuacao_estacao)
        progress_bar.progress(idx / total_estacoes, text="Processando critérios...")
    progress_bar.empty()
    
    colunas = list(get_args(NomeCampo))
    df_resultado = pd.DataFrame(pontuacoes)[colunas]
    df_resultado['Total'] = df_resultado[colunas[1:]].sum(axis=1)
    
    return df_resultado
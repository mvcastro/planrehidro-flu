import warnings
from typing import Callable, Sequence

import numpy as np
import pandas as pd

from planrehidro_flu.core.models import CurvaDeDescarga, ResumoDeDescarga
from planrehidro_flu.databases.hidro.models import PivotCota, PivotVazao


def pivot_vazao_to_dataframe(serie_vazao: Sequence[PivotVazao]) -> pd.DataFrame:
    dataframe = pd.DataFrame(
        [
            {
                "data": row.Data,
                "vazao": row.Vazao,
                "nivel_consistencia": row.NivelConsistencia,
            }
            for row in serie_vazao
        ]
    )
    dataframe["data"] = pd.to_datetime(dataframe["data"])
    df_serie = (
        dataframe.dropna()
        .sort_values(["data", "nivel_consistencia"])
        .drop_duplicates(subset=["data"], keep="last")
        .set_index("data")
    )

    return df_serie


def pivot_cota_to_dataframe(serie_vazao: Sequence[PivotCota]) -> pd.DataFrame:
    dataframe = pd.DataFrame(
        [
            {
                "data": row.Data,
                "cota": row.Cota,
                "nivel_consistencia": row.NivelConsistencia,
            }
            for row in serie_vazao
        ]
    )
    dataframe["data"] = pd.to_datetime(dataframe["data"])
    df_serie = (
        dataframe.dropna()
        .sort_values(["data", "nivel_consistencia"])
        .drop_duplicates(subset=["data"], keep="last")
        .set_index("data")
    )

    return df_serie


def retorna_estatisticas_descarga_liquida(
    resumo_descarga: list[ResumoDeDescarga], ano_referencia: int
) -> tuple[float, float]:
    if not resumo_descarga:
        raise ValueError("Nenhum resumo de descarga encontrado para o código fornecido")

    total_medicoes = len(resumo_descarga)
    ano_minimo = min(descarga.data.year for descarga in resumo_descarga)
    medicoes_por_ano = total_medicoes / (ano_referencia - ano_minimo)

    return total_medicoes, medicoes_por_ano


def retorna_equacao_potencial_curva_chave(
    coef_a: float, coef_h0: float, coef_n: float
) -> Callable[[float], float]:
    def equacao(cota: float) -> float:
        if cota <= coef_h0:
            return 0.0
        return coef_a * (cota - coef_h0) ** coef_n

    return equacao


def calcula_desvio_medio_curva_chave(
    resumo_descarga: list[ResumoDeDescarga], curvas_descarga: list[CurvaDeDescarga]
) -> float:
    if not resumo_descarga:
        raise ValueError("A lista com o resumo de descarga está vazia")

    if not curvas_descarga:
        raise ValueError("A lista com as curvas de descarga está vazia")

    desvios: list[float] = []

    for descarga in resumo_descarga:
        if descarga.vazao is None or descarga.vazao == 0.0:
            warnings.warn("Descarga no resumo de descarga encontrada com vazão nula!")
            continue

        curva_descarga = [
            curva
            for curva in curvas_descarga
            if curva.data_validade_inicio <= descarga.data <= curva.data_validade_fim
            and curva.cota_minima <= descarga.cota <= curva.cota_maxima
        ]

        if not curva_descarga:
            print(
                f"Nenhuma curva de descarga válida encontrada para a data {descarga.data} e cota {descarga.cota}"
            )
            continue

        curva_selecionada = curva_descarga[0]
        coeficientes = [
            curva_selecionada.coef_a,
            curva_selecionada.coef_h0,
            curva_selecionada.coef_n,
        ]

        if any([coef is None for coef in coeficientes]):
            raise ValueError(
                f"Coeficientes inválidos para equação de curva chave: a={curva_selecionada.coef_a}, H0={curva_selecionada.coef_h0}, N={curva_selecionada.coef_n}"
            )

        equacao = retorna_equacao_potencial_curva_chave(*coeficientes)  # type: ignore
        descarga_calculada = equacao(descarga.cota / 100)
        desvios.append(100 * abs(descarga.vazao - descarga_calculada) / descarga.vazao)

    return float(np.mean(desvios))

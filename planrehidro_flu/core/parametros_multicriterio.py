from typing import Literal, TypedDict

from planrehidro_flu.core.parametros_calculo import (
    CalculoDoCriterio,
    CalculoDoCriterioAreaDrenagem,
    CalculoDoCriterioDescargaLiquida,
    CalculoDoCriterioDescargaLiquidaAnual,
    CalculoDoCriterioDesvioCurvaChave,
    CalculoDoCriterioExtensaoDaSerie,
    CalculoDoCriterioLocalizacaoSemiarido,
    CalculoDoCriterioProximidadeRHNR,
    CalculoDoCriterioTelemetrica,
    CalculoDoCriterioTotalDeDescargasLiquidas,
    CalculoDoCriterioTrechoDeNavegacao,
)

Grupo = Literal[
    "Localização da Estação",
    "Qualidade dos Dados da Estação",
]


class CriterioSelecionado(TypedDict):
    grupo: Grupo
    criterio: str
    unidade: str
    calculo: CalculoDoCriterio


parametros_multicriterio: list[CriterioSelecionado] = [
    {
        "grupo": "Localização da Estação",
        "criterio": "Área de drenagem da bacia à montante",
        "unidade": "km²",
        "calculo": CalculoDoCriterioAreaDrenagem(),
    },
    {
        "grupo": "Localização da Estação",
        "criterio": "Trecho usado para navegação",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTrechoDeNavegacao(),
    },
    {
        "grupo": "Localização da Estação",
        "criterio": "Localizada na região semiárida",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioLocalizacaoSemiarido(),
    },
    {
        "grupo": "Localização da Estação",
        "criterio": "Proximidade à estação da RHNR",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioProximidadeRHNR(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "criterio": "Extensão da série de dados",
        "unidade": "anos",
        "calculo": CalculoDoCriterioExtensaoDaSerie(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "criterio": "Descarga Líquida",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioDescargaLiquida(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "criterio": "Telemetria",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTelemetrica(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "criterio": "Desvio da Curva-Chave",
        "unidade": "percentual (%)",
        "calculo": CalculoDoCriterioDesvioCurvaChave(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "criterio": "Total de medições de descarga líquida",
        "unidade": "medições",
        "calculo": CalculoDoCriterioTotalDeDescargasLiquidas(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "criterio": "Medições de descarga líquida / Ano",
        "unidade": "medições/ano",
        "calculo": CalculoDoCriterioDescargaLiquidaAnual(),
    },
]

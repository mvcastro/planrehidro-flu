from typing import Literal, TypedDict

from planrehidro_flu.core.parametros_calculo import (
    CalculoDoCriterio,
    CalculoDoCriterioAreaDrenagem,
    CalculoDoCriterioDescargaLiquida,
    CalculoDoCriterioDescargaLiquidaAnual,
    CalculoDoCriterioDesvioCurvaChave,
    CalculoDoCriterioEmPoloDeIrrigacao,
    CalculoDoCriterioExtensaoDaSerie,
    CalculoDoCriterioISHNaAreaDrenagem,
    CalculoDoCriterioProximidadeRHNR,
    CalculoDoCriterioRelevanciaEspacial,
    CalculoDoCriterioTelemetrica,
    CalculoDoCriterioTotalDeDescargasLiquidas,
    CalculoDoCriterioTrechoDeNavegacao,
    CalculoDoCriterioTrechoVulnerabilidadeCheias,
)

Grupo = Literal[
    "Localização da Estação",
    "Objetivos da Estação",
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
        "criterio": "Relevância espacial",
        "unidade": "Nº estações / km²",
        "calculo": CalculoDoCriterioRelevanciaEspacial(),
    },
    {
        "grupo": "Objetivos da Estação",
        "criterio": "Trecho com vulnerabilidade a cheias",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTrechoVulnerabilidadeCheias(),
    },
    {
        "grupo": "Objetivos da Estação",
        "criterio": "ISH na área de drenagem",
        "unidade": "Quantitativo classificação",
        "calculo": CalculoDoCriterioISHNaAreaDrenagem(),
    },
    {
        "grupo": "Objetivos da Estação",
        "criterio": "Localizada em Polos Nacionais de Irrigação ",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioEmPoloDeIrrigacao(),
    },
    {
        "grupo": "Objetivos da Estação",
        "criterio": "Trecho usado para navegação",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTrechoDeNavegacao(),
    },
    # {
    #     "grupo": "Localização da Estação",
    #     "criterio": "Localizada na região semiárida",
    #     "unidade": "booleano",
    #     "calculo": CalculoDoCriterioLocalizacaoSemiarido(),
    # },
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

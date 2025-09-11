from typing import Literal, TypedDict

from planrehidro_flu.core.parametros_calculo import (
    CalculoDoCriterio,
    CalculoDoCriterioAreaDrenagem,
    CalculoDoCriterioLocalizacaoSemiarido,
    CalculoDoCriterioProximidadeRHNR,
    CalculoDoCriterioTrechoDeNavegacao,
)

Grupo = Literal[
    "Alocação da Estação",
    "Operação da Estação",
    "Dados da Estação",
]


class CriterioSelecionado(TypedDict):
    grupo: Grupo
    criterio: str
    unidade: str
    calculo: CalculoDoCriterio


parametros_multicriterio: list[CriterioSelecionado] = [
    {
        "grupo": "Alocação da Estação",
        "criterio": "Área de drenagem da bacia à montante",
        "unidade": "km²",
        "calculo": CalculoDoCriterioAreaDrenagem(),
    },
    {
        "grupo": "Alocação da Estação",
        "criterio": "Trecho usado para navegação",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTrechoDeNavegacao(),
    },
    {
        "grupo": "Alocação da Estação",
        "criterio": "Localizada na região semiárida",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioLocalizacaoSemiarido(),
    },
    {
        "grupo": "Alocação da Estação",
        "criterio": "Proximidade à estação da RHNR",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioProximidadeRHNR(),
    },
    {
        "grupo": "Operação da Estação",
        "criterio": "Idade",
        "unidade": "anos",
        "calculo": ,
    },
    {
        "grupo": "Operação da Estação",
        "criterio": "Descarga Líquida",
        "unidade": "booleano",
        "calculo": ,
    },
    {
        "grupo": "Operação da Estação",
        "criterio": "Telemetria",
        "unidade": "booleano",
        "calculo": ,
    },
    {
        "grupo": "Dados da Estação",
        "criterio": "Desvio da Curva-Chave",
        "unidade": "percentual (%)",
        "calculo": ,
    },
    {
        "grupo": "Dados da Estação",
        "criterio": "Total de medições de descarga líquida",
        "unidade": "medições",
        "calculo": ,
    },
    {
        "grupo": "Dados da Estação",
        "criterio": "Medições de descarga líquida / Ano",
        "unidade": "medições/ano",
        "calculo": ,
    },
]

from typing import Literal, TypedDict

from planrehidro_flu.core.parametros_calculo import (
    CalculoDoCriterio,
    CalculoDoCriterioAreaDrenagem,
    CalculoDoCriterioDescargaLiquidaAnual,
    CalculoDoCriterioDesvioCurvaChave,
    CalculoDoCriterioEmPoloDeIrrigacao,
    CalculoDoCriterioExtensaoDaSerie,
    CalculoDoCriterioISHNaAreaDrenagem,
    CalculoDoCriterioLocalizacaoSemiarido,
    CalculoDoCriterioProximidadeEstacaoSetorEletrico,
    CalculoDoCriterioRelevanciaEspacial,
    CalculoDoCriterioTrechoDeNavegacao,
    CalculoDoCriterioTrechoVulnerabilidadeCheias,
)

Grupo = Literal[
    "Localização da Estação",
    "Objetivos da Estação",
    "Qualidade dos Dados da Estação",
]


NomeCampo = Literal[
    "codigo_estacao",
    "area_dren",
    "espacial",
    "cheias",
    "ish",
    "semiarido",
    "irrigacao",
    "rhnr",
    "navegacao",
    "extensao",
    "desv_cchave",
    "med_desc",
    "est_energia",
]


class CriterioSelecionado(TypedDict):
    grupo: Grupo
    nome_campo: NomeCampo
    descricao: str
    unidade: str
    calculo: CalculoDoCriterio


parametros_multicriterio: list[CriterioSelecionado] = [
    {
        "grupo": "Localização da Estação",
        "nome_campo": "area_dren",
        "descricao": "Área de drenagem da bacia à montante",
        "unidade": "Km²",
        "calculo": CalculoDoCriterioAreaDrenagem(),
    },
    {
        "grupo": "Localização da Estação",
        "nome_campo": "espacial",
        "descricao": "Relevância espacial",
        "unidade": "Km² / Nº estações",
        "calculo": CalculoDoCriterioRelevanciaEspacial(),
    },
    {
        "grupo": "Objetivos da Estação",
        "nome_campo": "cheias",
        "descricao": "Trecho com vulnerabilidade a cheias",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTrechoVulnerabilidadeCheias(),
    },
    {
        "grupo": "Objetivos da Estação",
        "nome_campo": "ish",
        "descricao": "ISH na área de drenagem",
        "unidade": "Quantitativo classificação",
        "calculo": CalculoDoCriterioISHNaAreaDrenagem(),
    },
    {
        "grupo": "Localização da Estação",
        "nome_campo": "semiarido",
        "descricao": "Localizada na região semiárida",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioLocalizacaoSemiarido(),
    },
    {
        "grupo": "Objetivos da Estação",
        "nome_campo": "irrigacao",
        "descricao": "Localizada em Polos Nacionais de Irrigação",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioEmPoloDeIrrigacao(),
    },
    # {
    #     "grupo": "Localização da Estação",
    #     "nome_campo": "rhnr",
    #     "descricao": "Proximidade à estação da RHNR",
    #     "unidade": "objetivos da RHRN",
    #     "calculo": CalculoDoCriterioProximidadeObjetivosRHNR(),
    # },
    # {
    #     "grupo": "Localização da Estação",
    #     "nome_campo": "est_rhnr",
    #     "descricao": "Proximidade à estação da RHNR",
    #     "unidade": "booleano",
    #     "calculo": CalculoDoCriterioProximidadeEstacaoRHNR(),
    # },
    {
        "grupo": "Localização da Estação",
        "nome_campo": "est_energia",
        "descricao": "Proximidade à estação do Setor Elétrico",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioProximidadeEstacaoSetorEletrico(),
    },
    {
        "grupo": "Objetivos da Estação",
        "nome_campo": "navegacao",
        "descricao": "Trecho usado para navegação",
        "unidade": "booleano",
        "calculo": CalculoDoCriterioTrechoDeNavegacao(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "nome_campo": "extensao",
        "descricao": "Extensão da série de dados",
        "unidade": "Anos",
        "calculo": CalculoDoCriterioExtensaoDaSerie(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "nome_campo": "desv_cchave",
        "descricao": "Desvio da Curva-Chave",
        "unidade": "Percentual (%)",
        "calculo": CalculoDoCriterioDesvioCurvaChave(),
    },
    {
        "grupo": "Qualidade dos Dados da Estação",
        "nome_campo": "med_desc",
        "descricao": "Medições de descarga líquida / Ano",
        "unidade": "Medições/Ano",
        "calculo": CalculoDoCriterioDescargaLiquidaAnual(),
    },
    # {
    #     "grupo": "Qualidade dos Dados da Estação",
    #     "criterio": "Descarga Líquida",
    #     "unidade": "booleano",
    #     "calculo": CalculoDoCriterioDescargaLiquida(),
    # },
    # {
    #     "grupo": "Qualidade dos Dados da Estação",
    #     "criterio": "Telemetria",
    #     "unidade": "booleano",
    #     "calculo": CalculoDoCriterioTelemetrica(),
    # },
    # {
    #     "grupo": "Qualidade dos Dados da Estação",
    #     "criterio": "Total de medições de descarga líquida",
    #     "unidade": "medições",
    #     "calculo": CalculoDoCriterioTotalDeDescargasLiquidas(),
    # },
]

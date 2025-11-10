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
    CalculoDoCriterioProximidadeEstacaoRHNRCenario1,
    CalculoDoCriterioProximidadeEstacaoRHNRCenario2,
    CalculoDoCriterioProximidadeEstacaoSetorEletrico,
    CalculoDoCriterioRelevanciaEspacial,
    CalculoDoCriterioTrechoDeNavegacao,
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
    "ish",
    "semiarido",
    "irrigacao",
    "navegacao",
    "extensao",
    "desv_cchave",
    "med_desc",
    "est_energia",
    "rhnr_c1",
    "rhnr_c2",
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
        "unidade": "Adimensional",
        "calculo": CalculoDoCriterioRelevanciaEspacial(),
    },
    {
        "grupo": "Objetivos da Estação",
        "nome_campo": "ish",
        "descricao": "ISH na área de drenagem",
        "unidade": "Classificação ISH",
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
    {
        "grupo": "Localização da Estação",
        "nome_campo": "rhnr_c1",
        "descricao": "Proximidade à estação da RHNR - Cenário1",
        "unidade": "Relação entre áreas de drenagem (%)",
        "calculo": CalculoDoCriterioProximidadeEstacaoRHNRCenario1(),
    },
    {
        "grupo": "Localização da Estação",
        "nome_campo": "rhnr_c2",
        "descricao": "Proximidade à estação da RHNR - Cenário2",
        "unidade": "Relação entre áreas de drenagem (%)",
        "calculo": CalculoDoCriterioProximidadeEstacaoRHNRCenario2(),
    },
    {
        "grupo": "Localização da Estação",
        "nome_campo": "est_energia",
        "descricao": "Proximidade à estação do Setor Elétrico",
        "unidade": "Relação entre áreas de drenagem (%)",
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
]


def search_criterio_props(nome_campo: NomeCampo) -> CriterioSelecionado:
    for criterio in parametros_multicriterio:
        if criterio["nome_campo"] == nome_campo:
            return criterio
    raise ValueError(f"Critério {nome_campo} não encontrado.")

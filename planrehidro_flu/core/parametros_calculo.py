import calendar
import json
from abc import ABC, abstractmethod
from functools import cache
from typing import cast

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.params_funcoes_suporte import (
    calcula_desvio_medio_curva_chave,
    pivot_cota_to_dataframe,
    retorna_estatisticas_descarga_liquida,
)
from planrehidro_flu.databases.cplar.bd_cplar_reader import (
    PostgresReader,
    localiza_cocursodags_de_jusante,
)
from planrehidro_flu.databases.cplar.models import (
    EstacaoHidroRefBHAE,
    EstacaoHidroRefBHO2013,
)
from planrehidro_flu.databases.hidro.hidro_reader import HidroDWReader

CriterioOutput = int | float | bool | str | None


@cache
def create_cpalar_reader() -> PostgresReader:
    return PostgresReader()


@cache
def create_hidro_reader() -> HidroDWReader:
    return HidroDWReader()


class CalculoDoCriterio(ABC):
    @abstractmethod
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput: ...


class CalculoDoCriterioAreaDrenagem(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        if estacao.area_drenagem_km2 is None:
            raise ValueError("Área de drenagem não informada")
        return estacao.area_drenagem_km2


class CalculoDoCriterioRelevanciaEspacial(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        if estacao.area_drenagem_km2 is None:
            raise ValueError("Área de drenagem não informada")

        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHAE, codigo_estacao=estacao.codigo
        )
        estacoes_a_montante = cplar_reader.retorna_estacoes_de_montante(
            classe_href=EstacaoHidroRefBHAE, estacao_href=estacao_href
        )

        if not estacoes_a_montante:
            return 1.0

        estacoes_a_computar = []
        for est_mont in estacoes_a_montante:
            cocursodags_jusante = localiza_cocursodags_de_jusante(est_mont.cobacia)
            cobacias_jusante = [
                est_jus.codigo
                for est_jus in estacoes_a_montante
                if est_jus.cocursodag in cocursodags_jusante
                and est_jus.codigo != est_mont.codigo
                and est_jus.cobacia <= est_mont.cobacia
                and cast(float, est_jus.area_drenagem)
                > cast(float, est_mont.area_drenagem)
            ]
            if not cobacias_jusante:
                estacoes_a_computar.append(est_mont)

        soma_areas_drenagens_nao_repetidas = sum(
            set([cast(float, est.area_drenagem) for est in estacoes_a_computar])
        )

        return 1 - (soma_areas_drenagens_nao_repetidas / estacao.area_drenagem_km2)


class CalculoDoCriterioDensidadeEstacoes(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        if estacao.area_drenagem_km2 is None:
            raise ValueError("Área de drenagem não informada")

        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHAE, codigo_estacao=estacao.codigo
        )
        estacoes_a_montante = cplar_reader.retorna_estacoes_de_montante(
            classe_href=EstacaoHidroRefBHAE, estacao_href=estacao_href
        )
        if not estacoes_a_montante:
            return 0.0

        return estacao.area_drenagem_km2 / len(estacoes_a_montante)


class CalculoDoCriterioTrechoVulnerabilidadeCheias(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHO2013, codigo_estacao=estacao.codigo
        )
        trecho_vulneravel_cheias = cplar_reader.retorna_trecho_vulneravel_a_cheias(
            estacao_href.cobacia
        )
        return False if trecho_vulneravel_cheias is None else True


class CalculoDoCriterioISHNaAreaDrenagem(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHO2013, codigo_estacao=estacao.codigo
        )
        ish_cobacias = cplar_reader.retorna_classes_ish_numerico_por_area_drenagem(
            estacao_href.cobacia
        )
        if not ish_cobacias:
            raise ValueError(
                f"Ottobacias não encontradas para a estação: {estacao.codigo}"
            )
        area_total = sum([ish.ire_nuareacont for ish in ish_cobacias])
        ish_ponderado = (
            sum([ish.ire_cs_ishfinal * ish.ire_nuareacont for ish in ish_cobacias])
            / area_total
        )
        return self.classifica_resultado(ish_ponderado)

    def classifica_resultado(self, valor_ish: float) -> str:
        if 1.0 <= valor_ish < 1.5:
            return "Mínimo"
        if 1.5 <= valor_ish < 2.5:
            return "Baixo"
        if 2.5 <= valor_ish < 3.5:
            return "Médio"
        if 3.5 <= valor_ish < 4.5:
            return "Alto"
        if valor_ish >= 4.5:
            return "Máximo"
        raise ValueError(
            f"Valor de ISH inválido (válido entre 1 e 5): valor {valor_ish}"
        )


class CalculoDoCriterioEmPoloDeIrrigacao(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorno_polo_nacional_por_corrdenadas(
            latitude=estacao.latitude, longitude=estacao.longitude
        )
        return False if estacao_href is None else True


class CalculoDoCriterioTrechoDeNavegacao(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHO2013, codigo_estacao=estacao.codigo
        )
        trecho = cplar_reader.retorna_trecho_navegavel(estacao_href.cobacia)
        return False if trecho is None else True


class CalculoDoCriterioLocalizacaoSemiarido(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        if estacao.latitude is None or estacao.longitude is None:
            raise ValueError("Coordenadas da estação não informadas")
        cplar_reader = create_cpalar_reader()
        return cplar_reader.esta_no_semiarido(
            latitude=estacao.latitude, longitude=estacao.longitude
        )
        # geometria_semiarido = cplar_reader.retorna_geometria_semiarido()
        # ponto_estacao = gpd.points_from_xy([estacao.longitude], [estacao.latitude])[0]
        # return bool(geometria_semiarido.contains(ponto_estacao).any())


class CalculoDoCriterioProximidadeObjetivosRHNR(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        objetivos = cplar_reader.retorna_objetivos_rhnr(estacao.codigo)
        if not objetivos:
            return "Nenhum objetivo"

        objetivos_dict = {obj.criterio: obj.prop_areas for obj in objetivos}
        return json.dumps(objetivos_dict, ensure_ascii=False)


class CalculoDoCriterioProximidadeEstacaoRHNR(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro, **kwargs) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()

        if "cenario" not in kwargs:
            raise ValueError(
                "Cenário não informado para o cálculo de proximidade à RHNR"
            )
        cenario = kwargs["cenario"]

        if cenario == "Cenário 1":
            estacoes_rhnr = cplar_reader.retorna_estacoes_rhnr_cenario1()
        elif cenario == "Cenário 2":
            estacoes_rhnr = cplar_reader.retorna_estacoes_rhnr_cenario2()
        else:
            raise ValueError(
                f"Cenário inválido: {cenario} - Cenário deve ser 'Cenário 1' ou 'Cenário 2'"
            )

        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHAE, codigo_estacao=estacao.codigo
        )

        if estacao.area_drenagem_km2 is None:
            return None

        estacoes_montante = (
            cplar_reader.retorna_estacoes_hidrorreferenciadas_de_montante(
                classe_href=EstacaoHidroRefBHAE, cobacia=estacao_href.cobacia
            )
        )
        estacoes_jusante = cplar_reader.retorna_estacoes_hidrorreferenciadas_de_jusante(
            classe_href=EstacaoHidroRefBHAE, cobacia=estacao_href.cobacia
        )
        estacoes_no_rio = list(estacoes_montante) + list(estacoes_jusante)
        codigos_estacoes_rhnr = {est.codigo for est in estacoes_rhnr}
        estacoes_selecionadas = [
            100 * abs(1 - (est.area_drenagem / estacao.area_drenagem_km2))
            for est in estacoes_no_rio
            if est.codigo in codigos_estacoes_rhnr and est.area_drenagem is not None
        ]

        return min(estacoes_selecionadas) if estacoes_selecionadas else None


class CalculoDoCriterioProximidadeEstacaoRHNRCenario1(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        return CalculoDoCriterioProximidadeEstacaoRHNR().calcular(
            estacao, cenario="Cenário 1"
        )


class CalculoDoCriterioProximidadeEstacaoRHNRCenario2(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        return CalculoDoCriterioProximidadeEstacaoRHNR().calcular(
            estacao, cenario="Cenário 2"
        )


class CalculoDoCriterioProximidadeEstacaoSetorEletrico(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | None:
        cplar_reader = create_cpalar_reader()
        hidro_reader = create_hidro_reader()

        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(
            classe_href=EstacaoHidroRefBHAE, codigo_estacao=estacao.codigo
        )

        if estacao.area_drenagem_km2 is None:
            return None

        estacoes_montante = (
            cplar_reader.retorna_estacoes_hidrorreferenciadas_de_montante(
                classe_href=EstacaoHidroRefBHAE, cobacia=estacao_href.cobacia
            )
        )
        estacoes_jusante = cplar_reader.retorna_estacoes_hidrorreferenciadas_de_jusante(
            classe_href=EstacaoHidroRefBHAE,
            cobacia=estacao_href.cobacia,
        )

        estacoes_no_rio = {
            est.codigo: est.nuareamont for est in estacoes_montante + estacoes_jusante
            if est.codigo != estacao.codigo
        }
        estacoes_hidro = hidro_reader.retorna_estacoes_por_codigo(
            codigos=list(estacoes_no_rio.keys())
        )

        estacoes_hidro_energia = [
            est
            for est in estacoes_hidro
            if est.TipoRedeEnergetica == 1 and est.Operando == 1
        ]

        if not estacoes_hidro_energia:
            return None

        proporcao_area_estacoes_setor_eletrico = []
        for est in estacoes_hidro_energia:
            if est.AreaDrenagem is None:
                area_drenagem = estacoes_no_rio.get(est.Codigo, None)
                if area_drenagem is None:
                    continue
            else:
                area_drenagem = est.AreaDrenagem

            proporcao_area = 100 * abs(1 - (area_drenagem / estacao.area_drenagem_km2))
            proporcao_area_estacoes_setor_eletrico.append(proporcao_area)

        return (
            min(proporcao_area_estacoes_setor_eletrico)
            if proporcao_area_estacoes_setor_eletrico
            else None
        )


class CalculoDoCriterioExtensaoDaSerie(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro, **kwargs) -> CriterioOutput:
        hidro_reader = create_hidro_reader()
        serie_historica = hidro_reader.retorna_serie_historica_cota(estacao.codigo)
        percentual_falhas = kwargs.get("percentual_falhas")
        limiar_falhas = percentual_falhas / 100 if percentual_falhas else 0.1

        if not serie_historica:
            print(
                f"Nenhum dado da série histórica disponível para a estação {estacao.codigo}"
            )
            return 0

        df_serie = pivot_cota_to_dataframe(serie_historica)
        anos_disponiveis = df_serie.index.year.value_counts()  # type: ignore
        anos_completos = []
        ano_inicial = anos_disponiveis.index.min()
        ano_final = anos_disponiveis.index.max()
        for ano in range(ano_inicial, ano_final + 1):
            total_dias_no_ano = 366 if calendar.isleap(ano) else 365
            total_dias_disponiveis = anos_disponiveis.get(ano, 0)
            if (1 - (total_dias_disponiveis / total_dias_no_ano)) <= limiar_falhas:
                anos_completos.append(ano)

        return len(anos_completos)


class CalculoDoCriterioDescargaLiquida(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        return True if resumo_de_descarga else False


class CalculoDoCriterioTelemetrica(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        return estacao.estacao_telemetrica


class CalculoDoCriterioDesvioCurvaChave(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        curva_de_descarga = hidro_reader.retorna_curva_de_descarga(estacao.codigo)

        if not resumo_de_descarga:
            print(
                f"Nenhum medição de descarga disponível para a estação {estacao.codigo}"
            )
            print("Não é possível calcular o desvio da curva chave -> Retornando nulo")
            return None

        if not curva_de_descarga:
            print(
                f"Nenhuma curva de descarga disponível para a estação {estacao.codigo}"
            )
            print("Não é possível calcular o desvio da curva chave -> Retornando nulo")
            return None

        return calcula_desvio_medio_curva_chave(resumo_de_descarga, curva_de_descarga)


class CalculoDoCriterioTotalDeDescargasLiquidas(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        estats = retorna_estatisticas_descarga_liquida(
            resumo_de_descarga, ano_referencia=2024
        )
        return estats[0]


class CalculoDoCriterioDescargaLiquidaAnual(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )

        if not resumo_de_descarga:
            print(
                f"Nenhum medição de descarga disponível para a estação {estacao.codigo}"
            )
            print(
                "Não é possível calcular a média anual do número de descargas líquidas -> Retornando 0.0!"
            )
            return 0.0

        estats = retorna_estatisticas_descarga_liquida(
            resumo_descarga=[
                resumo for resumo in resumo_de_descarga if resumo.data.year <= 2024
            ],
            ano_referencia=2024,
        )
        return estats[1]

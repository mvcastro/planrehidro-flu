import calendar
import json
from abc import ABC, abstractmethod
from functools import cache

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.params_funcoes_suporte import (
    calcula_desvio_medio_curva_chave,
    pivot_cota_to_dataframe,
    retorna_estatisticas_descarga_liquida,
)
from planrehidro_flu.databases.cplar.bd_cplar_reader import PostgresReader
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
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(estacao.codigo)
        estacoes_a_montante = cplar_reader.retorna_estacoes_de_montante(
            estacao_href.cobacia
        )
        if not estacoes_a_montante:
            return 0.0

        return estacao.area_drenagem_km2 / len(estacoes_a_montante)


class CalculoDoCriterioTrechoVulnerabilidadeCheias(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(estacao.codigo)
        trecho_vulneravel_cheias = cplar_reader.retorna_trecho_vulneravel_a_cheias(
            estacao_href.cobacia
        )
        return False if trecho_vulneravel_cheias is None else True


class CalculoDoCriterioISHNaAreaDrenagem(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(estacao.codigo)
        ish_cobacias = cplar_reader.retorna_classes_ish_por_area_drenagem(
            estacao_href.cobacia
        )

        classes_ish = {
            "Alto": 0.0,
            "Baixo": 0.0,
            "Máximo": 0.0,
            "Médio": 0.0,
            "Mínimo": 0.0,
        }

        for ish in ish_cobacias:
            if ish.brasil is None:
                continue
            classes_ish[ish.brasil] += ish.nuareacont

        classes_ish = {classe: round(valor, 1) for classe, valor in classes_ish.items()}

        return json.dumps(classes_ish, ensure_ascii=False)


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
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(estacao.codigo)
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


class CalculoDoCriterioProximidadeRHNR(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> CriterioOutput:
        cplar_reader = create_cpalar_reader()
        objetivos = cplar_reader.retorna_objetivos_rhnr(estacao.codigo)
        if not objetivos:
            return "Nenhum objetivo"

        objetivos_dict = {obj.criterio: obj.prop_areas for obj in objetivos}
        return json.dumps(objetivos_dict, ensure_ascii=False)


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
        estats = retorna_estatisticas_descarga_liquida(resumo_de_descarga)
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

        estats = retorna_estatisticas_descarga_liquida(resumo_de_descarga)
        return estats[1]

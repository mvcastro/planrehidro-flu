from abc import ABC, abstractmethod
from datetime import date, timedelta
from functools import cache

import geopandas as gpd

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.params_funcoes_suporte import (
    calcula_desvio_medio_curva_chave,
    pivot_vazao_to_dataframe,
    retorna_estatisticas_descarga_liquida,
)
from planrehidro_flu.databases.cplar.bd_cplar_reader import PostgresReader
from planrehidro_flu.databases.hidro.hidro_reader import HidroDWReader


@cache
def create_cpalar_reader() -> PostgresReader:
    return PostgresReader()


@cache
def create_hidro_reader() -> HidroDWReader:
    return HidroDWReader()


class CalculoDoCriterio(ABC):
    @abstractmethod
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str: ...


class CalculoDoCriterioAreaDrenagem(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        if estacao.area_drenagem_km2 is None:
            raise ValueError("Área de drenagem não informada")
        return estacao.area_drenagem_km2


class CalculoDoCriterioTrechoDeNavegacao(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        cplar_reader = create_cpalar_reader()
        estacao_href = cplar_reader.retorna_estacao_hidrorreferenciada(estacao.codigo)
        trecho = cplar_reader.existe_trecho_navegavel(estacao_href.cobacia)
        return False if trecho is None else True


class CalculoDoCriterioLocalizacaoSemiarido(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        if estacao.latitude is None or estacao.longitude is None:
            raise ValueError("Coordenadas da estação não informadas")
        cplar_reader = create_cpalar_reader()
        geometria_semiarido = cplar_reader.retorna_geometria_semiarido()
        ponto_estacao = gpd.points_from_xy([estacao.longitude], [estacao.latitude])[0]
        return bool(geometria_semiarido.contains(ponto_estacao).any())


class CalculoDoCriterioProximidadeRHNR(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        cplar_reader = create_cpalar_reader()
        objetivos = cplar_reader.retorna_objetivos_rhnr(estacao.codigo)
        return ", ".join(objetivos) if objetivos else "Nenhum objetivo"


class CalculoDoCriterioExtensaoDaSerie(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro, **kwargs) -> float | bool | str:
        hidro_reader = create_hidro_reader()
        serie_historica = hidro_reader.retorna_serie_historica(estacao.codigo)
        percentual_falhas = kwargs.get("percentual_falhas")
        limiar_falhas = percentual_falhas / 100 if percentual_falhas else 0.1

        if not serie_historica:
            raise ValueError("Nenhum dado disponível para a estação")

        df_serie = pivot_vazao_to_dataframe(serie_historica)
        anos_disponiveis = df_serie.index.year.value_counts()  # type: ignore
        anos_completos = []
        ano_inicial = anos_disponiveis.index.min()
        ano_final = anos_disponiveis.index.max()
        for ano in range(ano_inicial, ano_final + 1):
            total_dias_no_ano = (
                date(ano, 12, 31) - date(ano, 1, 1) + timedelta(days=1)
            ).days
            if (1 - (anos_disponiveis[ano] / total_dias_no_ano)) >= limiar_falhas:
                anos_completos.append(ano)

        return len(anos_completos)


class CalculoDoCriterioDescargaLiquida(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        return True if resumo_de_descarga else False


class CalculoDoCriterioTelemetrica(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        return estacao.estacao_telemetrica


class CalculoDoCriterioDesvioCurvaChave(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        curva_de_descarga = hidro_reader.retorna_curva_de_descarga(estacao.codigo)

        return calcula_desvio_medio_curva_chave(resumo_de_descarga, curva_de_descarga)


class CalculoDoCriterioTotalDeDescargasLiquidas(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        estats = retorna_estatisticas_descarga_liquida(tuple(resumo_de_descarga))
        return estats[0]


class CalculoDoCriterioDescargaLiquidaAnual(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | bool | str:
        hidro_reader = create_hidro_reader()
        resumo_de_descarga = hidro_reader.retorna_resumo_de_descarga(
            codigo=estacao.codigo
        )
        estats = retorna_estatisticas_descarga_liquida(tuple(resumo_de_descarga))
        return estats[1]

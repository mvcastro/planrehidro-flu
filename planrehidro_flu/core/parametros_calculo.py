from abc import ABC, abstractmethod

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.databases.cplar.bd_cplar_reader import PostgresReader
import geopandas as gpd
CPLAR_READER = PostgresReader()

class CalculoDoCriterio(ABC):
    @abstractmethod
    def calcular(self, estacao: EstacaoHidro) -> float | str: ...


class CalculoDoCriterioAreaDrenagem(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | str:
        if estacao.area_drenagem_km2 is None:
            raise ValueError("Área de drenagem não informada")
        return estacao.area_drenagem_km2


class CalculoDoCriterioTrechoDeNavegacao(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | str:
        estacao_href = CPLAR_READER.retorna_estacao_hidrorreferenciada(
            estacao.codigo
        )
        trecho = CPLAR_READER.existe_trecho_navegavel(estacao_href.cobacia)
        return "Sim" if trecho else "Não"

class CalculoDoCriterioLocalizacaoSemiarido(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | str:
        if estacao.latitude is None or estacao.longitude is None:
            raise ValueError("Coordenadas da estação não informadas")
        geometria_semiarido = CPLAR_READER.retorna_geometria_semiarido()
        ponto_estacao = gpd.points_from_xy([estacao.longitude], [estacao.latitude])[0]
        return "Sim" if geometria_semiarido.contains(ponto_estacao).any() else "Não"
    
class CalculoDoCriterioProximidadeRHNR(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | str:
        objetivos = CPLAR_READER.retorna_objetivos_rhnr(estacao.codigo)
        return ", ".join(objetivos) if objetivos else "Nenhum objetivo"
    
class CalculoDoCriterioIdadeEstacao(CalculoDoCriterio):
    def calcular(self, estacao: EstacaoHidro) -> float | str:
        ...  # Implementação futura
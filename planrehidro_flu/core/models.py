from datetime import date
from typing import Literal, Self

from pydantic import BaseModel, PositiveFloat

from planrehidro_flu.core.enums import (
    BaciaEnumStr,
    EstadoEnumStr,
)
from planrehidro_flu.databases.hidro.enums import TipoEstacao


class EstacaoHidro(BaseModel):
    codigo: int
    nome: str
    latitude: float
    longitude: float
    altitude: float | None
    area_drenagem_km2: float | None
    bacia: str
    subbacia: str
    rio: str | None
    estado: str
    municipio: str
    responsavel: str
    tipo_estacao: TipoEstacao
    estacao_telemetrica: bool
    operando: bool


class ResumoDeDescarga(BaseModel):
    codigo: int
    nivel_consistencia: Literal[1, 2]
    data: date
    cota: float
    vazao: None | float
    area_molhada: None |  float
    largura: None |  float
    vel_media: None |  float
    profundidade: None |  float


class CurvaDeDescarga(BaseModel):
    codigo: int
    nivel_consistencia: Literal[1, 2]
    data_validade_inicio: date
    data_validade_fim: date
    cota_maxima: float
    cota_minima: float
    tipo_curva: Literal[1, 2, 3, 4, 5, 6]
    tipo_equacao: Literal[1, 2, 3, 4]
    coef_a: float | None
    coef_h0: float | None
    coef_n: float | None
    coef_a0: float | None
    coef_a1: float | None
    coef_a2: float | None
    coef_a3: float | None


class InventarioEstacoesHidro:
    def __init__(self, lista_estacoes: list[EstacaoHidro]):
        self._inventario = lista_estacoes

    @property
    def inventario(self) -> list[EstacaoHidro]:
        return self._inventario

    def filtra_responsavel(self, responsavel: str) -> Self:
        return self.__class__(
            [
                estacao
                for estacao in self.inventario
                if estacao.responsavel == responsavel
            ]
        )

    def filtra_bacia(self, bacia: BaciaEnumStr) -> Self:
        return self.__class__(
            [estacao for estacao in self.inventario if estacao.bacia == bacia]
        )

    def filtra_estado(self, estado: EstadoEnumStr) -> Self:
        return self.__class__(
            [estacao for estacao in self.inventario if estacao.estado == estado]
        )

    def filtra_estacao_por_codigo(self, codigo: int) -> EstacaoHidro:
        for estacao in self.inventario:
            if estacao.codigo == codigo:
                return estacao

        raise ValueError(f"Estação com código {codigo} não encontrada.")

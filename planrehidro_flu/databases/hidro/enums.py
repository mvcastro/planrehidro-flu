from enum import Enum, IntEnum
from typing import Literal

NomeDaTabela = Literal["Chuvas", "Vazoes", "Cotas"]
NomeDaTabelaPivot = Literal["Chuva", "Vazao", "Cota"]

TIPOS_DADOS_ESTACAO: dict[int, NomeDaTabelaPivot] = {
    1: "Vazao",
    2: "Chuva",
}


class TipoDeDados(Enum):
    COTA = 1
    CHUVA = 2
    VAZAO = 3


class NivelDeConsistencia(Enum):
    BRUTO = 1
    CONSISTIDO = 2


class TipoDaEstacao(Enum):
    FLU = 1
    PLU = 2


class TipoEstacao(IntEnum):
    FLUVIOMETRICA = 1
    PLUVIOMETRICA = 2


class BaciaEnum(IntEnum):
    RIO_AMAZONAS = 1
    RIO_TOCANTINS = 2
    ATLANTICO_TRECHO_NORTE_NORDESTE = 3
    RIO_SAO_FRANCISCO = 4
    ATLANTICO_TRECHO_LESTE = 5
    RIO_PARANA = 6
    RIO_URUGUAI = 7
    ATLANTICO_TRECHO_SUDESTE = 8
    OUTRAS = 9


class EstadoEnum(IntEnum):
    RONDONIA = 1
    ACRE = 2
    AMAZONAS = 3
    RORAIMA = 4
    PARA = 5
    AMAPA = 6
    MARANHAO = 7
    PIAUI = 8
    CEARA = 9
    RIO_GRANDE_DO_NORTE = 10
    PARAIBA = 11
    PERNAMBUCO = 12
    ALAGOAS = 13
    SERGIPE = 15
    BAHIA = 16
    MINAS_GERAIS = 17
    ESPIRITO_SANTO = 18
    RIO_DE_JANEIRO = 19
    SAO_PAULO = 21
    PARANA = 22
    SANTA_CATARINA = 23
    RIO_GRANDE_DO_SUL = 24
    MATO_GROSSO_DO_SUL = 25
    GOIAS = 26
    DISTRITO_FEDERAL = 27


class NivelConsistencia(IntEnum):
    BRUTO = 1
    CONSISTIDO = 2
    
class Responsavel(IntEnum):
    ANA = 1
    DNOS = 2
    DNIT = 3
    CODEVASF = 4
    INMET = 5
    CESP = 6
    CEEE = 7
    LIGHT = 8
    FUNCEME = 9
    DAEE = 10
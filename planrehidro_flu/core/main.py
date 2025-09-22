from tqdm import tqdm

from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.parametros_multicriterio import (
    CriterioSelecionado,
    parametros_multicriterio,
)
from planrehidro_flu.databases.hidro.enums import Responsavel, TipoEstacao
from planrehidro_flu.databases.hidro.hidro_reader import HidroDWReader
from planrehidro_flu.databases.internal.database_access import (
    insere_criterios_da_estacao,
    insere_inventario,
    retorna_estacoes_processadas,
    update_criterio_da_estacao,
)
from planrehidro_flu.databases.internal.models import ENGINE, Base, CriteriosDaEstacao


def create_tables() -> None:
    Base.metadata.create_all(ENGINE)  # Create tables if they don't exist


def armazena_inventario(inventario: list[EstacaoHidro]) -> None:
    insere_inventario(engine=ENGINE, inventario=inventario)


def main() -> None:
    create_tables()
    hidro = HidroDWReader()
    inventario = hidro.cria_inventario_estacao_hidro(
        tipo_estacao=TipoEstacao.FLUVIOMETRICA,
        operando=True,
        responsavel=Responsavel.ANA,
    )
    # armazena_inventario(inventario)

    estacoes_processadas = retorna_estacoes_processadas(engine=ENGINE)
    estacoes_nao_processadas = [
        estacao for estacao in inventario if estacao.codigo not in estacoes_processadas
    ]

    for estacao in tqdm(estacoes_nao_processadas):
        try:
            valores_criterios = {}
            valores_criterios["codigo_estacao"] = estacao.codigo

            for criterio in parametros_multicriterio:
                valor_criterio = criterio["calculo"].calcular(estacao)
                valores_criterios[criterio["nome_campo"]] = valor_criterio  # type: ignore

            insere_criterios_da_estacao(
                engine=ENGINE, valores_criterios=CriteriosDaEstacao(**valores_criterios)
            )
        except Exception as e:
            print(f"Erro ao processar critérios para a estação {estacao.codigo}: {e}")
            print(f"{criterio['nome_campo']}")


def update_field(criterio: CriterioSelecionado):
    hidro = HidroDWReader()
    inventario = hidro.cria_inventario_estacao_hidro(
        tipo_estacao=TipoEstacao.FLUVIOMETRICA,
        operando=True,
        responsavel=Responsavel.ANA,
    )

    for estacao in tqdm(inventario):
        try:
            valores_criterios = {}
            valores_criterios["codigo_estacao"] = estacao.codigo

            valor_criterio = criterio["calculo"].calcular(estacao)
            valores_criterios[criterio["nome_campo"]] = valor_criterio  # type: ignore

            update_criterio_da_estacao(
                engine=ENGINE,
                codigo_estacao=estacao.codigo,
                campo=criterio["nome_campo"],
                valor=valor_criterio,
            )
        except Exception as e:
            print(
                f"Erro ao processar critério: {criterio['nome_campo']} para a estação {estacao.codigo}: {e}"
            )


if __name__ == "__main__":
    # create_tables()
    main()

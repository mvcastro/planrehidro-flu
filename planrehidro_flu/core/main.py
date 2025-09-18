from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.parametros_multicriterio import parametros_multicriterio
from planrehidro_flu.databases.hidro.enums import Responsavel, TipoEstacao
from planrehidro_flu.databases.hidro.hidro_reader import HidroDWReader
from planrehidro_flu.databases.internal.database_access import (
    insere_criterio,
    insere_inventario,
)
from planrehidro_flu.databases.internal.models import ENGINE, Base


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

    for estacao in inventario:
        for criterio in parametros_multicriterio:
            valor_criterio = criterio["calculo"].calcular(estacao)
            insere_criterio(
                engine=ENGINE,
                codigo_estacao=estacao.codigo,
                criterio_selecionado=criterio,
                valor_criterio=valor_criterio,
            )


if __name__ == "__main__":
    main()

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


def armazena_inventario() -> None:
    hidro = HidroDWReader()
    inventario = hidro.cria_inventario_estacao_hidro(
        tipo_estacao=TipoEstacao.FLUVIOMETRICA,
        operando=True,
        responsavel=Responsavel.ANA,
    )
    insere_inventario(engine=ENGINE, inventario=inventario)


def main() -> None:
    create_tables()
    # armazena_inventario()

    # insere_criterio(
    #     engine=ENGINE,
    #     codigo_estacao=1234,
    #     criterio_selecionado=parametros_multicriterio[0],
    #     valor_criterio=57.4,
    # )

    insere_criterio(
        engine=ENGINE,
        codigo_estacao=2345,
        criterio_selecionado=parametros_multicriterio[1],
        valor_criterio=123.5,
    )

    # for estacao in inventario:
    #     ...


if __name__ == "__main__":
    main()

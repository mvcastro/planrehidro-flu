from sqlalchemy.orm import Session

from planrehidro_flu.databases.cplar.bd_cplar_reader import PostgresReader
from planrehidro_flu.databases.internal.models import (
    ENGINE,
    Base,
    CenarioEstacaoesRHNR,
    # InventarioEstacaoFluAna,
)


def migra_dados_dos_bancos():
    # BD Bases CPLAR
    postgres_reader = PostgresReader()
    # inventario = postgres_reader.retorna_dados_adicionais_estacoes()
    estacoes_cenario1 = postgres_reader.retorna_estacoes_rhnr_cenario1()
    estacoes_cenario2 = postgres_reader.retorna_estacoes_rhnr_cenario2()
    codigos_cenario1 = [estacao.codigo for estacao in estacoes_cenario1]
    codigos_cenario2 = [estacao.codigo for estacao in estacoes_cenario2]
    codigos_estacoes = set(codigos_cenario1 + codigos_cenario2)

    # BD Interno
    Base.metadata.create_all(bind=ENGINE)
    # inventario_sqlite = [InventarioEstacaoFluAna(**estacao) for estacao in inventario]

    # with Session(ENGINE) as session:
    #     session.add_all(inventario_sqlite)
    #     session.commit()

    with Session(ENGINE) as session:
        for codigo in codigos_estacoes:
            eh_cenario1 = codigo in codigos_cenario1
            eh_cenario2 = codigo in codigos_cenario2
            session.add(
                CenarioEstacaoesRHNR(
                    codigo_estacao=codigo, cenario1=eh_cenario1, cenario2=eh_cenario2
                )
            )
        session.commit()


if __name__ == "__main__":
    migra_dados_dos_bancos()

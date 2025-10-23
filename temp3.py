from planrehidro_flu.core.models import EstacaoHidro
from planrehidro_flu.core.parametros_calculo import CalculoDoCriterioISHNaAreaDrenagem, CalculoDoCriterioTrechoDeNavegacao
from planrehidro_flu.databases.cplar.bd_cplar_reader import PostgresReader
from planrehidro_flu.databases.hidro.enums import TipoEstacao

postgres_reader = PostgresReader()

# classes = postgres_reader.retorna_classes_ish_numerico_por_area_drenagem(
#     cobacia="86999782"
# )

# print([classe.ire_cs_ishfinal for classe in classes])

estacao_hidro = EstacaoHidro(
    codigo=19500000,
    nome="",
    latitude=0.0,
    longitude=0.0,
    altitude=None,
    area_drenagem_km2=132.0,
    bacia="",
    subbacia="",
    rio=None,
    estado="",
    municipio="",
    responsavel="ANA",
    tipo_estacao=TipoEstacao.FLUVIOMETRICA,
    estacao_telemetrica=False,
    operando=True,
)


# print(CalculoDoCriterioISHNaAreaDrenagem().calcular(estacao_hidro))
print(CalculoDoCriterioTrechoDeNavegacao().calcular(estacao_hidro))
from planrehidro_flu.core.parametros_multicriterio import NomeCampo

type Classe = list[tuple[float | None, float | None, float]]
type Params = dict[NomeCampo, Classe]

DEFAULT_WEIGTH_PARAMS: dict[NomeCampo, int] = {
    "area_dren": 1,
    "espacial": 1,
    "ish": 1,
    "irrigacao": 1,
    "est_energia": 1,
    "cheias": 1,
    "navegacao": 1,
    "extensao": 1,
    "desv_cchave": 1,
    "med_desc": 1,
}

DEFAULT_PARAMS_CLASSES: Params = {
    "area_dren": [
        (0.0, 500.0, 0.0),
        (500.0, 1000.0, 1.0),
        (1000.0, 1500.0, 2.0),
        (1500.000, None, 3.0),
    ],
    "espacial": [(0.0, 0.25, 0.0), (0.25, 0.50, 2.0), (0.5, None, 3.0)],
    "extensao": [
        (0.0, 10.0, 0.0),
        (10.0, 20.0, 1.0),
        (20.0, 30.0, 2.0),
        (30.0, None, 3.0),
    ],
    "desv_cchave": [
        (12.0, None, 0.0),
        (8.0, 12.0, 1.0),
        (6.0, 8.0, 2.0),
        (0.0, 6.0, 3.0),
    ],
    "med_desc": [
        (0.0, 3.0, 0.0),
        (3.0, 4.0, 2.0),
        (4.0, None, 3.0),
    ],
}

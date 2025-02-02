def yhdista(*listat: list) -> list:
    uusi_lista = []
    for lista in listat:
        uusi_lista.extend(lista)
    return uusi_lista


def pyorista(luku: float) -> int:
    desimaalit = luku - int(luku)
    if desimaalit < 0.5:
        return int(luku)
    else:
        return int(luku) + 1

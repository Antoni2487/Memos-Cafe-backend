import re

DNI_REGEX = re.compile(r"^\d{8}$")
RUC_REGEX = re.compile(r"^\d{11}$")


def es_dni_valido(valor: str) -> bool:
    return bool(DNI_REGEX.match(valor or ""))


def es_ruc_valido(valor: str) -> bool:
    return bool(RUC_REGEX.match(valor or ""))

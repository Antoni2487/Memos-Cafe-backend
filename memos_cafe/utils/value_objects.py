from memos_cafe.utils.validators import es_dni_valido, es_ruc_valido


class DocumentoIdentidad:
    """Value object: un DNI o RUC ya validado y normalizado.

    Inmutable adrede — no expone setters, solo lectura vía las
    properties tipo/valor. Dos documentos son iguales si tienen el
    mismo tipo y el mismo valor, sin importar la instancia; por eso
    __eq__/__hash__ se basan en esos dos campos, no en identidad de
    objeto (comportamiento por defecto de Python).
    """

    DNI = "dni"
    RUC = "ruc"
    TIPOS_VALIDOS = (DNI, RUC)

    def __init__(self, tipo: str, valor: str):
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de documento inválido: {tipo!r}")

        valor_normalizado = (valor or "").strip()
        if tipo == self.DNI and not es_dni_valido(valor_normalizado):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos.")
        if tipo == self.RUC and not es_ruc_valido(valor_normalizado):
            raise ValueError("El RUC debe tener exactamente 11 dígitos numéricos.")

        self._tipo = tipo
        self._valor = valor_normalizado

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def valor(self) -> str:
        return self._valor

    def __eq__(self, other):
        if not isinstance(other, DocumentoIdentidad):
            return NotImplemented
        return self._tipo == other._tipo and self._valor == other._valor

    def __hash__(self):
        return hash((self._tipo, self._valor))

    def __repr__(self):
        return f"DocumentoIdentidad(tipo={self._tipo!r}, valor={self._valor!r})"

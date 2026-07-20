import pytest

from memos_cafe.utils.value_objects import DocumentoIdentidad


class TestDocumentoIdentidadContratoDeIgualdad:
    """Verifica que __eq__/__hash__ cumplen el contrato de igualdad de
    Python: reflexividad, simetría, consistencia con hash, y que nunca
    es igual a None ni a un objeto de otro tipo. No usa la base de
    datos: DocumentoIdentidad es un objeto Python puro."""

    @pytest.fixture
    def dni(self):
        return DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")

    def test_reflexividad(self, dni):
        assert dni == dni

    def test_simetria(self):
        a = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        b = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        assert a == b
        assert b == a

    def test_consistencia_con_hash(self):
        a = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        b = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        assert a == b
        assert hash(a) == hash(b)

    def test_no_es_igual_a_none(self, dni):
        assert dni != None  # noqa: E711 — a propósito: probamos __eq__, no "is"
        assert not (dni == None)  # noqa: E711

    def test_no_es_igual_a_objeto_de_otro_tipo(self, dni):
        assert dni != "12345678"
        assert dni != 12345678
        assert dni != object()

    def test_documentos_con_distinto_valor_no_son_iguales(self):
        a = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        b = DocumentoIdentidad(DocumentoIdentidad.DNI, "87654321")
        assert a != b

    def test_documentos_con_distinto_tipo_no_son_iguales(self):
        dni = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        ruc = DocumentoIdentidad(DocumentoIdentidad.RUC, "12345678901")
        assert dni != ruc

    def test_usable_como_clave_de_set_sin_duplicar_iguales(self):
        """Consecuencia directa de un __hash__ consistente con __eq__:
        dos documentos iguales colapsan a un solo elemento en un set."""
        a = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        b = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        c = DocumentoIdentidad(DocumentoIdentidad.RUC, "12345678901")
        assert {a, b, c} == {a, c}
        assert len({a, b, c}) == 2


class TestDocumentoIdentidadValidacion:
    """DocumentoIdentidad no se puede construir en un estado invalido —
    la validacion vive en el constructor, no aparte."""

    def test_dni_valido_se_construye(self):
        doc = DocumentoIdentidad(DocumentoIdentidad.DNI, "12345678")
        assert doc.tipo == "dni"
        assert doc.valor == "12345678"

    def test_ruc_valido_se_construye(self):
        doc = DocumentoIdentidad(DocumentoIdentidad.RUC, "12345678901")
        assert doc.tipo == "ruc"
        assert doc.valor == "12345678901"

    def test_normaliza_espacios(self):
        doc = DocumentoIdentidad(DocumentoIdentidad.DNI, "  12345678  ")
        assert doc.valor == "12345678"

    @pytest.mark.parametrize("valor_invalido", [
        pytest.param("1234567", id="7-digitos"),
        pytest.param("123456789", id="9-digitos"),
        pytest.param("1234567A", id="con-letras"),
        pytest.param("", id="vacio"),
    ])
    def test_dni_invalido_lanza_error(self, valor_invalido):
        with pytest.raises(ValueError, match="DNI"):
            DocumentoIdentidad(DocumentoIdentidad.DNI, valor_invalido)

    @pytest.mark.parametrize("valor_invalido", [
        pytest.param("1234567890", id="10-digitos"),
        pytest.param("123456789012", id="12-digitos"),
        pytest.param("1234567890A", id="con-letras"),
        pytest.param("", id="vacio"),
    ])
    def test_ruc_invalido_lanza_error(self, valor_invalido):
        with pytest.raises(ValueError, match="RUC"):
            DocumentoIdentidad(DocumentoIdentidad.RUC, valor_invalido)

    def test_tipo_invalido_lanza_error(self):
        with pytest.raises(ValueError, match="Tipo de documento"):
            DocumentoIdentidad("pasaporte", "12345678")

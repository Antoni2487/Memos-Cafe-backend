from memos_cafe.mesas.models import Mesa


class MesaService:
    @staticmethod
    def crear(numero: int, capacidad: int) -> Mesa:
        if Mesa.objects.filter(numero=numero).exists():
            raise ValueError(f"Ya existe una mesa con el número {numero}.")
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor a 0.")
        return Mesa.objects.create(numero=numero, capacidad=capacidad)

    @staticmethod
    def actualizar(mesa: Mesa, numero: int = None, capacidad: int = None) -> Mesa:
        if numero and numero != mesa.numero:
            if Mesa.objects.filter(numero=numero).exists():
                raise ValueError(f"Ya existe una mesa con el número {numero}.")
            mesa.numero = numero
        if capacidad is not None:
            if capacidad <= 0:
                raise ValueError("La capacidad debe ser mayor a 0.")
            mesa.capacidad = capacidad
        mesa.save(update_fields=["numero", "capacidad"])
        return mesa

    @staticmethod
    def dar_de_baja(mesa: Mesa) -> Mesa:
        if mesa.estado == Mesa.Estado.OCUPADA:
            raise ValueError(
                f"No se puede dar de baja la mesa {mesa.numero} porque está ocupada."
            )
        mesa.dar_de_baja()
        return mesa

    @staticmethod
    def cambiar_estado(mesa: Mesa, nuevo_estado: str) -> Mesa:
        """Cambio manual de estado (endpoint PATCH /mesas/{id}/estado/).

        'ocupada' NUNCA es un destino valido aqui: una mesa se ocupa
        unicamente como consecuencia de crear una orden (Mesa.ocupar()),
        nunca por accion manual del mesero/admin.
        'libre' tampoco es alcanzable manualmente desde 'ocupada': se
        libera automaticamente al cobrar o anular la orden asociada
        (Mesa.liberar()). Desde 'ocupada' no hay transicion manual posible.

        Las unicas transiciones manuales permitidas son reservar y
        cancelar una reserva.
        """
        transiciones_validas = {
            Mesa.Estado.LIBRE: [Mesa.Estado.RESERVADA],
            Mesa.Estado.RESERVADA: [Mesa.Estado.LIBRE],
            Mesa.Estado.OCUPADA: [],
        }
        if nuevo_estado not in transiciones_validas.get(mesa.estado, []):
            raise ValueError(
                f"No se puede cambiar el estado de '{mesa.estado}' a '{nuevo_estado}' manualmente."
            )
        mesa.estado = nuevo_estado
        mesa.save(update_fields=["estado"])
        return mesa

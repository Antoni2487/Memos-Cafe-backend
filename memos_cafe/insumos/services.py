from decimal import Decimal

from memos_cafe.insumos.models import RegistroInsumo, TipoInsumo


class TipoInsumoService:
    @staticmethod
    def crear(
        nombre: str,
        unidad: str,
        stock_minimo: Decimal = Decimal("0"),
    ) -> TipoInsumo:
        if TipoInsumo.objects.filter(nombre__iexact=nombre).exists():
            raise ValueError(f"Ya existe un insumo con el nombre '{nombre}'.")
        if stock_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")
        return TipoInsumo.objects.create(
            nombre=nombre,
            unidad=unidad,
            stock_minimo=stock_minimo,
        )

    @staticmethod
    def desactivar(insumo: TipoInsumo) -> TipoInsumo:
        insumo.activo = False
        insumo.save(update_fields=["activo"])
        return insumo
    
    @staticmethod
    def editar(insumo, **kwargs):
        nombre = kwargs.get("nombre")
        if nombre and TipoInsumo.objects.filter(nombre__iexact=nombre).exclude(pk=insumo.pk).exists():
            raise ValueError(f"Ya existe un insumo con el nombre '{nombre}'.")
        stock_minimo = kwargs.get("stock_minimo")
        if stock_minimo is not None and stock_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")
        for campo, valor in kwargs.items():
            if valor is not None:
                setattr(insumo, campo, valor)
        insumo.save()
        return insumo

    @staticmethod
    def activar(insumo):
        insumo.activo = True
        insumo.save(update_fields=["activo"])
        return insumo


class RegistroInsumoService:
    @staticmethod
    def registrar_compra(
        insumo: TipoInsumo,
        usuario,
        cantidad: Decimal,
        costo_unitario: Decimal,
        proveedor: str = "",
        observaciones: str = "",
    ) -> RegistroInsumo:
        """
        Registra una compra de insumo y actualiza el stock automáticamente.
        Los registros son inmutables — no hay update ni delete.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        if costo_unitario <= 0:
            raise ValueError("El costo unitario debe ser mayor a 0.")

        return RegistroInsumo.objects.create(
            insumo=insumo,
            usuario=usuario,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            proveedor=proveedor,
            observaciones=observaciones,
        )
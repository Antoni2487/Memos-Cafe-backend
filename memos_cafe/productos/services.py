from decimal import Decimal

from django.utils import timezone

from memos_cafe.productos.models import Categoria, Producto, Promocion


class CategoriaService:
    @staticmethod
    def crear(nombre: str) -> Categoria:
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise ValueError(f"Ya existe una categoría con el nombre '{nombre}'.")
        return Categoria.objects.create(nombre=nombre)

    @staticmethod
    def editar(categoria, nombre: str):
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=categoria.pk).exists():
            raise ValueError(f"Ya existe una categoría con el nombre '{nombre}'.")
        categoria.nombre = nombre
        categoria.save(update_fields=["nombre"])
        return categoria

    @staticmethod
    def activar(categoria: Categoria) -> Categoria:
        categoria.activo = True
        categoria.save(update_fields=["activo"])
        return categoria

    @staticmethod
    def desactivar(categoria: Categoria) -> Categoria:
        """
        Desactiva una categoría.
        Lanza ValueError si tiene productos disponibles asociados.
        """
        if categoria.productos.filter(disponible=True).exists():
            raise ValueError(
                f"No se puede desactivar '{categoria.nombre}' "
                f"porque tiene productos disponibles asociados."
            )
        categoria.activo = False
        categoria.save(update_fields=["activo"])
        return categoria


class ProductoService:
    @staticmethod
    def crear(
        nombre: str,
        precio: Decimal,
        categoria: Categoria,
        descripcion: str = "",
        disponible: bool = True,   
        imagen=None,
    ) -> Producto:
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return Producto.objects.create(
            nombre=nombre,
            precio=precio,
            categoria=categoria,
            descripcion=descripcion,
             disponible=disponible,  
            imagen=imagen,
        )

    @staticmethod
    def editar(producto: Producto, **kwargs) -> Producto:
        precio = kwargs.get("precio")
        if precio is not None and precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        for campo, valor in kwargs.items():
                setattr(producto, campo, valor)
        producto.save()
        return producto

    @staticmethod
    def actualizar_precio(producto: Producto, nuevo_precio: Decimal) -> Producto:
        if nuevo_precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        producto.precio = nuevo_precio
        producto.save(update_fields=["precio"])
        return producto


class PromocionService:
    @staticmethod
    def crear(
        nombre: str,
        precio: Decimal,
        fecha_inicio,
        fecha_fin,
        descripcion: str = "",
        imagen=None,
    ) -> Promocion:
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        if fecha_inicio < timezone.localdate():
            raise ValueError(
                "No se pueden crear promociones con fecha de inicio en el pasado."
            )
        if fecha_fin < fecha_inicio:
            raise ValueError(
                "La fecha de fin no puede ser anterior a la de inicio."
            )
        return Promocion.objects.create(
            nombre=nombre,
            precio=precio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            descripcion=descripcion,
            imagen=imagen,
        )

    @staticmethod
    def editar(promocion: Promocion, **kwargs) -> Promocion:
        precio = kwargs.get("precio")
        if precio is not None and precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        fecha_inicio = kwargs.get("fecha_inicio", promocion.fecha_inicio)
        fecha_fin = kwargs.get("fecha_fin", promocion.fecha_fin)
        if fecha_fin < fecha_inicio:
            raise ValueError("La fecha de fin no puede ser anterior a la de inicio.")
        for campo, valor in kwargs.items():
            if valor is not None:
                setattr(promocion, campo, valor)
        promocion.save()
        return promocion

    @staticmethod
    def activar(promocion: Promocion) -> Promocion:
        promocion.activo = True
        promocion.save(update_fields=["activo"])
        return promocion

    @staticmethod
    def desactivar(promocion: Promocion) -> Promocion:
        promocion.activo = False
        promocion.save(update_fields=["activo"])
        return promocion

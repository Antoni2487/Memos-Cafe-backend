from decimal import Decimal

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
        imagen_url: str = "",
    ) -> Producto:
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return Producto.objects.create(
            nombre=nombre,
            precio=precio,
            categoria=categoria,
            descripcion=descripcion,
            imagen_url=imagen_url,
        )

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
        imagen_url: str = "",
    ) -> Promocion:
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
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
            imagen_url=imagen_url,
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
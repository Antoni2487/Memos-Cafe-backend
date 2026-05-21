from rest_framework.viewsets import ModelViewSet

from memos_cafe_backend.productos.models import Categoria
from memos_cafe_backend.productos.models import Producto
from memos_cafe_backend.productos.models import Promocion
from memos_cafe_backend.productos.api.serializers import CategoriaSerializer
from memos_cafe_backend.productos.api.serializers import ProductoSerializer
from memos_cafe_backend.productos.api.serializers import ProductoWriteSerializer
from memos_cafe_backend.productos.api.serializers import PromocionSerializer
from memos_cafe_backend.utils.permissions import EsAdmin
from memos_cafe_backend.utils.permissions import TodosAutenticados


class CategoriaViewSet(ModelViewSet):
    """
    list/retrieve → todos los roles
    create/update/destroy → solo admin
    """
    queryset = Categoria.objects.filter(activo=True).order_by("nombre")
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        return [EsAdmin()]


class ProductoViewSet(ModelViewSet):
    """
    list/retrieve → todos los roles (solo disponibles)
    create/update/destroy → solo admin
    """
    serializer_class = ProductoSerializer

    def get_queryset(self):
        # Admin ve todos, el resto solo los disponibles
        if self.request.user.groups.filter(name="admin").exists():
            return Producto.objects.select_related("categoria").all()
        return Producto.objects.select_related("categoria").filter(disponible=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        return [EsAdmin()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductoWriteSerializer
        return ProductoSerializer


class PromocionViewSet(ModelViewSet):
    """
    list/retrieve → todos los roles (solo vigentes)
    create/update/destroy → solo admin
    """
    serializer_class = PromocionSerializer

    def get_queryset(self):
        # Admin ve todas, el resto solo las vigentes
        if self.request.user.groups.filter(name="admin").exists():
            return Promocion.objects.all()
        from django.utils import timezone
        hoy = timezone.localdate()
        return Promocion.objects.filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        )

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        return [EsAdmin()]
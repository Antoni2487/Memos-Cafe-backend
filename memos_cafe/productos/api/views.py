from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from memos_cafe.productos.models import Categoria, Producto, Promocion
from memos_cafe.productos.services import CategoriaService, ProductoService, PromocionService
from memos_cafe.productos.api.serializers import (
    CategoriaSerializer,
    ProductoSerializer,
    ProductoWriteSerializer,
    PromocionSerializer,
    PromocionWriteSerializer,
)
from memos_cafe.utils.permissions import EsAdmin, TodosAutenticados


class CategoriaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name="admin").exists():
            return Categoria.objects.all()
        return Categoria.objects.filter(activo=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        return [EsAdmin()]

    @action(detail=False, methods=["post"], url_path="crear", permission_classes=[EsAdmin])
    def crear(self, request):
        """POST /api/productos/categorias/crear/"""
        serializer = CategoriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            categoria = CategoriaService.crear(
                nombre=serializer.validated_data["nombre"]
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="desactivar", permission_classes=[EsAdmin])
    def desactivar(self, request, pk=None):
        """POST /api/productos/categorias/{id}/desactivar/"""
        categoria = self.get_object()
        try:
            CategoriaService.desactivar(categoria)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CategoriaSerializer(categoria).data)


class ProductoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    def get_queryset(self):
        if self.request.user.groups.filter(name="admin").exists():
            return Producto.objects.con_categoria()
        return Producto.objects.disponibles()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        return [EsAdmin()]

    def get_serializer_class(self):
        return ProductoSerializer

    @action(detail=False, methods=["post"], url_path="crear", permission_classes=[EsAdmin])
    def crear(self, request):
        """POST /api/productos/crear/"""
        serializer = ProductoWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            producto = ProductoService.crear(**serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="precio", permission_classes=[EsAdmin])
    def actualizar_precio(self, request, pk=None):
        """PATCH /api/productos/{id}/precio/"""
        producto = self.get_object()
        precio = request.data.get("precio")
        if not precio:
            return Response(
                {"detail": "El campo 'precio' es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from decimal import Decimal
            ProductoService.actualizar_precio(producto, Decimal(str(precio)))
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ProductoSerializer(producto).data)

    @action(detail=True, methods=["post"], url_path="desactivar", permission_classes=[EsAdmin])
    def desactivar(self, request, pk=None):
        """POST /api/productos/{id}/desactivar/"""
        producto = self.get_object()
        producto.desactivar()
        return Response(ProductoSerializer(producto).data)

    @action(detail=True, methods=["post"], url_path="activar", permission_classes=[EsAdmin])
    def activar(self, request, pk=None):
        """POST /api/productos/{id}/activar/"""
        producto = self.get_object()
        producto.activar()
        return Response(ProductoSerializer(producto).data)


class PromocionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    def get_queryset(self):
        if self.request.user.groups.filter(name="admin").exists():
            return Promocion.objects.all()
        return Promocion.objects.vigentes()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [TodosAutenticados()]
        return [EsAdmin()]

    def get_serializer_class(self):
        return PromocionSerializer

    @action(detail=False, methods=["post"], url_path="crear", permission_classes=[EsAdmin])
    def crear(self, request):
        """POST /api/productos/promociones/crear/"""
        serializer = PromocionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            promocion = PromocionService.crear(**serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PromocionSerializer(promocion).data, status=status.HTTP_201_CREATED)
from rest_framework.routers import DefaultRouter
from memos_cafe.roles.api.views import PermisoRolViewSet

router = DefaultRouter()
router.register(r"permisos", PermisoRolViewSet, basename="permiso-rol")

urlpatterns = router.urls

from auditlog.middleware import AuditlogMiddleware
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuditlogMiddleware(AuditlogMiddleware):
    """
    Extiende AuditlogMiddleware para capturar el usuario
    autenticado via JWT (Bearer token) en lugar de sesión Django.
    """

    def _get_actor(self, request):
        # Primero intenta el método original (sesión Django)
        actor = super()._get_actor(request)
        if actor is not None:
            return actor

        # Si no hay actor, intenta con JWT
        try:
            jwt_auth = JWTAuthentication()
            result = jwt_auth.authenticate(request)
            if result is not None:
                user, _ = result
                return user
        except Exception:
            pass

        return None

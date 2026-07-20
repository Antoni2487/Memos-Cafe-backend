class APICSPMiddleware:
    """Agrega Content-Security-Policy a las respuestas de /api/.

    Encontrado por un escaneo OWASP ZAP: la API no enviaba cabecera CSP
    (CWE-693). Se restringe solo a /api/ -- ahi todo son respuestas JSON,
    asi que "default-src 'none'" es seguro. No se toca /django-admin-panel/
    ni el resto del sitio para no arriesgar romper la UI del admin de Django
    (que puede depender de estilos/scripts inline) sin poder probarlo a fondo.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            response["Content-Security-Policy"] = "default-src 'none'"
        return response

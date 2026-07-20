#!/usr/bin/env bash
# Escaneo dinamico autenticado con OWASP ZAP contra la API REST de Django.
#
# Que hace:
#   1. Levanta el stack con docker compose (si no esta arriba).
#   2. Provisiona (idempotente) un usuario de prueba desechable y obtiene
#      un JWT real via POST /api/auth/login/.
#   3. Corre zap-full-scan.py (imagen oficial zaproxy/zap-stable) contra la
#      API, inyectando "Authorization: Bearer <token>" en cada request via
#      el addon Replacer de ZAP.
#   4. Guarda el reporte HTML y JSON en reportes/.
#   5. Corre zap_check_high_risk.py sobre el JSON: exit 1 si hay alguna
#      alerta de riesgo High (pensado para usarse como gate en CI).
#
# El exit code final de este script es el del gate (paso 5), no el de
# zap-full-scan.py: zap-full-scan.py devuelve codigos basados en sus propias
# reglas de alert-filter (WARN/FAIL de su config), un concepto distinto al
# "hay algo High si o no" que pide este gate.
#
# Variables de entorno configurables (todas opcionales, valores por defecto
# pensados para levantar todo localmente sin tocar nada mas):
#   COMPOSE_FILE      (default: docker-compose.local.yml)
#   DJANGO_CONTAINER  (default: memos_cafe_local_django)
#   APP_PORT          (default: 8000)
#   TARGET_URL        (default: http://host.docker.internal:${APP_PORT}/api/)
#   ZAP_IMAGE         (default: zaproxy/zap-stable)
#   ZAP_TEST_EMAIL    (default: zap.scan@test.local)
#   ZAP_TEST_PASSWORD (default: ZapScan-Local-2026!)
#   ZAP_TEST_ROLE     (default: admin — maximiza la superficie autenticada cubierta)
#
# Cualquier argumento extra pasado a este script se reenvia tal cual a
# zap-full-scan.py, por ejemplo para acotar el tiempo del spider:
#   ./scripts/zap_scan.sh -m 5
#
# Requiere: docker, docker compose (v2). No requiere python/jq en el host:
# el parseo del JSON de login y el gate final corren dentro del contenedor
# Django, que ya tiene Python (mismo patron que el resto del proyecto).

set -euo pipefail

# En Git Bash (MSYS) para Windows, rutas tipo "/zap/wrk" o "/app/..." pasadas
# como argumento se auto-traducen a rutas de Windows (ej. "/app/x" ->
# "C:/Program Files/Git/app/x"), rompiendo los -v y las rutas dentro de los
# contenedores. No-op en Linux/macOS.
export MSYS_NO_PATHCONV=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.local.yml}"
DJANGO_CONTAINER="${DJANGO_CONTAINER:-memos_cafe_local_django}"
APP_PORT="${APP_PORT:-8000}"
TARGET_URL="${TARGET_URL:-http://host.docker.internal:${APP_PORT}/api/}"
ZAP_IMAGE="${ZAP_IMAGE:-zaproxy/zap-stable}"
ZAP_TEST_EMAIL="${ZAP_TEST_EMAIL:-zap.scan@test.local}"
ZAP_TEST_PASSWORD="${ZAP_TEST_PASSWORD:-ZapScan-Local-2026!}"
ZAP_TEST_ROLE="${ZAP_TEST_ROLE:-admin}"
REPORTES_DIR="$PROJECT_ROOT/reportes"

log() { printf '[zap_scan] %s\n' "$1"; }

log "Levantando el stack (${COMPOSE_FILE})..."
docker compose -f "$COMPOSE_FILE" up -d

log "Esperando a que Django responda en el puerto ${APP_PORT}..."
# Probe TCP puro (bash /dev/tcp), no HTTP: /api/auth/login/ tiene throttle de
# "anon: 20/minute" (ver DEFAULT_THROTTLE_RATES en config/settings/base.py) y
# no queremos que el propio health-check consuma esa cuota antes del login real.
intentos=0
until (exec 3<>"/dev/tcp/localhost/${APP_PORT}") 2>/dev/null; do
  exec 3<&- 3>&- 2>/dev/null || true
  intentos=$((intentos + 1))
  if [ "$intentos" -ge 30 ]; then
    log "Django no respondio despues de 60s. Aborta."
    exit 1
  fi
  sleep 2
done
exec 3<&- 3>&- 2>/dev/null || true
log "Django arriba."

log "Provisionando usuario de prueba (${ZAP_TEST_EMAIL}, rol=${ZAP_TEST_ROLE})..."
docker exec -i \
  -e ZAP_TEST_EMAIL="$ZAP_TEST_EMAIL" \
  -e ZAP_TEST_PASSWORD="$ZAP_TEST_PASSWORD" \
  -e ZAP_TEST_ROLE="$ZAP_TEST_ROLE" \
  "$DJANGO_CONTAINER" python manage.py shell <<'PYEOF'
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
email = os.environ["ZAP_TEST_EMAIL"]
password = os.environ["ZAP_TEST_PASSWORD"]
role = os.environ["ZAP_TEST_ROLE"]

user, created = User.objects.get_or_create(email=email, defaults={"name": "ZAP Scan Bot"})
user.set_password(password)
user.is_active = True
user.save()

grupo, _ = Group.objects.get_or_create(name=role)
user.groups.add(grupo)

print(f"[zap_scan] usuario de prueba listo (creado={created}): {email} / rol={role}")
PYEOF

log "Obteniendo JWT via POST /api/auth/login/..."
# El probe TCP previo solo confirma que el puerto acepta conexiones, no que
# el proceso WSGI ya esta listo para responder (justo despues de un arranque
# en frio puede devolver "empty reply from server" un par de veces). Se
# reintenta con backoff en vez de fallar al primer intento.
LOGIN_RESPONSE=""
intentos_login=0
while true; do
  set +e
  LOGIN_RESPONSE="$(curl -s -X POST "http://localhost:${APP_PORT}/api/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${ZAP_TEST_EMAIL}\",\"password\":\"${ZAP_TEST_PASSWORD}\"}")"
  CURL_EXIT=$?
  set -e
  if [ "$CURL_EXIT" -eq 0 ] && [ -n "$LOGIN_RESPONSE" ]; then
    break
  fi
  intentos_login=$((intentos_login + 1))
  if [ "$intentos_login" -ge 5 ]; then
    log "curl no obtuvo respuesta del login tras 5 intentos (ultimo exit code: ${CURL_EXIT})."
    exit 1
  fi
  sleep 3
done

ACCESS_TOKEN="$(printf '%s' "$LOGIN_RESPONSE" | sed -n 's/.*"access":"\([^"]*\)".*/\1/p')"

if [ -z "$ACCESS_TOKEN" ]; then
  log "No se pudo obtener el access token. Respuesta del login:"
  printf '%s\n' "$LOGIN_RESPONSE"
  exit 1
fi
log "Token obtenido (${#ACCESS_TOKEN} caracteres)."

mkdir -p "$REPORTES_DIR"

# Nombre fijo (en vez de dejar que Docker le ponga uno al azar) para poder
# detectar y limpiar una corrida anterior que haya quedado huerfana (p.ej.
# si este script fue interrumpido a mitad de camino): --rm solo limpia el
# contenedor cuando el PROCESO DENTRO de el termina, no cuando se mata el
# cliente "docker run" que lo lanzo, asi que un corte externo puede dejar
# un escaneo zombie corriendo y compitiendo por el mismo servidor Django.
ZAP_CONTAINER_NAME="zap_full_scan_memos_cafe"
if docker ps -a --format '{{.Names}}' | grep -qx "$ZAP_CONTAINER_NAME"; then
  log "Encontrado un contenedor de una corrida anterior (${ZAP_CONTAINER_NAME}). Eliminando..."
  docker rm -f "$ZAP_CONTAINER_NAME" >/dev/null
fi

log "Lanzando zap-full-scan.py contra ${TARGET_URL}..."
set +e
docker run --rm \
  --name "$ZAP_CONTAINER_NAME" \
  --add-host=host.docker.internal:host-gateway \
  -v "$REPORTES_DIR:/zap/wrk:rw" \
  -t "$ZAP_IMAGE" zap-full-scan.py \
  -t "$TARGET_URL" \
  -r zap_report.html \
  -J zap_report.json \
  -z "-config replacer.full_list(0).description=auth -config replacer.full_list(0).enabled=true -config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchstr=Authorization -config replacer.full_list(0).regex=false -config replacer.full_list(0).replacement=Bearer\ ${ACCESS_TOKEN}" \
  "$@"
ZAP_EXIT_CODE=$?
set -e
log "zap-full-scan.py termino con exit code ${ZAP_EXIT_CODE} (informativo, no es el gate final)."

if [ ! -f "$REPORTES_DIR/zap_report.json" ]; then
  log "No se genero reportes/zap_report.json. Abortando antes del gate."
  exit 1
fi
log "Reportes guardados en ${REPORTES_DIR}/zap_report.html y ${REPORTES_DIR}/zap_report.json"

log "Evaluando alertas de riesgo High..."
set +e
docker exec "$DJANGO_CONTAINER" python /app/scripts/zap_check_high_risk.py /app/reportes/zap_report.json
GATE_EXIT_CODE=$?
set -e

exit "$GATE_EXIT_CODE"

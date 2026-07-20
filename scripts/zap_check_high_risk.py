#!/usr/bin/env python
"""Gate de CI: falla si el reporte JSON de OWASP ZAP tiene alertas de riesgo High.

Uso:
    python zap_check_high_risk.py <ruta-al-reporte.json>

Exit code 0  -> no hay alertas riskcode=3 (High) en el reporte.
Exit code 1  -> se encontro al menos una alerta High (detalle impreso en stdout).
Exit code 2  -> uso incorrecto o reporte inválido/no encontrado.

Solo usa stdlib para poder correr con cualquier interprete Python (incluido
el del contenedor Django del proyecto), sin depender de que el entorno que
lanza el scan tenga Python instalado.
"""

import json
import sys

RISKCODE_HIGH = "3"  # ZAP: 0=Info 1=Low 2=Medium 3=High


def alertas_high(reporte: dict) -> list[dict]:
    encontradas = []
    for site in reporte.get("site", []):
        nombre_site = site.get("@name", "")
        for alerta in site.get("alerts", []):
            if str(alerta.get("riskcode", "")) != RISKCODE_HIGH:
                continue
            instancias = alerta.get("instances") or [{}]
            encontradas.append(
                {
                    "nombre": alerta.get("alert") or alerta.get("name") or "(sin nombre)",
                    "url": instancias[0].get("uri", nombre_site),
                    "confianza": alerta.get("confidence", "?"),
                    "cwe": alerta.get("cweid", "?"),
                    "descripcion": (alerta.get("desc") or "").split("\n")[0][:200],
                }
            )
    return encontradas


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python zap_check_high_risk.py <reporte.json>", file=sys.stderr)
        return 2

    ruta = sys.argv[1]
    try:
        with open(ruta, encoding="utf-8") as f:
            reporte = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"No se pudo leer el reporte '{ruta}': {e}", file=sys.stderr)
        return 2

    altas = alertas_high(reporte)

    if not altas:
        print("OK: no se encontraron alertas de riesgo High en el escaneo ZAP.")
        return 0

    print(f"FALLO: {len(altas)} alerta(s) de riesgo High encontradas:\n")
    for a in altas:
        print(f"  - [{a['nombre']}] {a['url']}")
        print(f"    CWE-{a['cwe']} | confianza={a['confianza']}")
        if a["descripcion"]:
            print(f"    {a['descripcion']}")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())

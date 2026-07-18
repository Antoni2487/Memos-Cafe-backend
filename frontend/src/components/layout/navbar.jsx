import { useState, useEffect, useRef } from "react";
import { Bell, ShoppingBag, Receipt } from "lucide-react";
import authService from "../../services/authService";
import { useReloj } from "../../hooks/useReloj";
import api from "../../services/api";

const ICONO_CONFIG = {
  caja: { color: "#2C5545", bg: "rgba(44,85,69,0.1)" },
  orden: { color: "#1565c0", bg: "rgba(21,101,192,0.1)" },
  venta: { color: "#C9A84C", bg: "rgba(201,168,76,0.1)" },
};

function formatHora(iso) {
  return new Date(iso).toLocaleTimeString("es-PE", {
    hour: "2-digit", minute: "2-digit", hour12: true,
  });
}

// ── Inicializa el timestamp UNA sola vez cuando el módulo se carga ──────────
if (!localStorage.getItem("notif_ultima_lectura")) {
  localStorage.setItem("notif_ultima_lectura", new Date().toISOString());
}

export default function Navbar() {
  const user = authService.getUser();
  const ahora = useReloj();
  const esAdmin = user?.roles?.includes("admin");

  const [alertas, setAlertas] = useState([]);
  const [abierto, setAbierto] = useState(false);
  const [ultimaLectura, setUltimaLectura] = useState(
    () => localStorage.getItem("notif_ultima_lectura")
  );
  const dropdownRef = useRef(null);

  const initials = user?.nombre
    ? user.nombre.split(" ").slice(0, 2).map((n) => n[0]).join("").toUpperCase()
    : "U";

  // ── Polling cada 30 segundos ──────────────────────────────────────────────
  const cargarAlertas = async () => {
    if (!esAdmin) return;
    try {
      const { data } = await api.get("/alertas/");
      setAlertas(data);
    } catch { /* silencioso */ }
  };

  useEffect(() => {
    if (!esAdmin) return;
    cargarAlertas();
    const iv = setInterval(cargarAlertas, 30000);
    return () => clearInterval(iv);
  }, [esAdmin]);

  // ── Cerrar al hacer clic fuera ────────────────────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target))
        setAbierto(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // ── Marcar todas como leídas ──────────────────────────────────────────────
  const marcarTodasLeidas = () => {
    const ts = new Date().toISOString();
    setUltimaLectura(ts);
    localStorage.setItem("notif_ultima_lectura", ts);
  };

  // Solo cuentan las alertas POSTERIORES al último timestamp
  const noLeidas = alertas.filter(
    (a) => new Date(a.fecha) > new Date(ultimaLectura)
  ).length;

  return (
    <header
      className="flex items-center justify-between px-8 shrink-0"
      style={{
        backgroundColor: "#F8F4EE",
        borderBottom: "1px solid rgba(44,85,69,0.12)",
        height: "64px",
        position: "relative",
        zIndex: 100,
      }}
    >
      {/* Fecha y hora */}
      <div>
        <p style={{
          fontFamily: "'Lato', sans-serif", fontSize: 12.5,
          color: "#2C5545", fontWeight: 500, margin: 0, textTransform: "capitalize",
        }}>
          {ahora.toLocaleDateString("es-PE", {
            weekday: "long", day: "numeric", month: "long", year: "numeric",
          })}
        </p>
        <p style={{
          fontFamily: "'Lato', sans-serif", fontSize: 11.5,
          color: "rgba(44,85,69,0.6)", margin: 0,
        }}>
          Lima, Perú — {ahora.toLocaleTimeString("es-PE", {
            hour: "2-digit", minute: "2-digit", hour12: true,
          })}
        </p>
      </div>

      <div className="flex items-center gap-4">

        {/* ── Campana ── */}
        {esAdmin && (
          <div ref={dropdownRef} style={{ position: "relative" }}>
            <button
              onClick={() => {
                const next = !abierto;
                setAbierto(next);
                if (next) marcarTodasLeidas();
              }}
              className="relative rounded-full flex items-center justify-center"
              style={{ width: 38, height: 38, backgroundColor: "rgba(44,85,69,0.07)", border: "none", cursor: "pointer" }}
            >
              <Bell size={17} strokeWidth={1.8} style={{ color: "#2C5545" }} />
              {noLeidas > 0 && (
                <span style={{
                  position: "absolute", top: 6, right: 6,
                  width: 16, height: 16, borderRadius: "50%",
                  backgroundColor: "#c62828", color: "white",
                  fontFamily: "'Lato', sans-serif", fontSize: 9,
                  fontWeight: 700, display: "flex",
                  alignItems: "center", justifyContent: "center",
                }}>
                  {noLeidas > 9 ? "9+" : noLeidas}
                </span>
              )}
            </button>

            {/* Dropdown */}
            {abierto && (
              <div style={{
                position: "absolute", top: 46, right: 0,
                width: 340, backgroundColor: "white",
                borderRadius: 12, boxShadow: "0 8px 32px rgba(0,0,0,0.14)",
                border: "1px solid rgba(44,85,69,0.1)",
                overflow: "hidden", zIndex: 200,
              }}>
                <div style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid rgba(44,85,69,0.08)",
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                }}>
                  <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 14, fontWeight: 600, color: "#2C5545" }}>
                    Notificaciones
                  </span>
                  <span style={{ fontFamily: "'Lato', sans-serif", fontSize: 11, color: "rgba(44,85,69,0.5)" }}>
                    Últimas 8 horas
                  </span>
                </div>

                <div style={{ maxHeight: 380, overflowY: "auto" }}>
                  {alertas.length === 0 ? (
                    <div style={{
                      padding: "32px 16px", textAlign: "center",
                      fontFamily: "'Lato', sans-serif", fontSize: 13,
                      color: "rgba(44,85,69,0.4)",
                    }}>
                      Sin notificaciones recientes
                    </div>
                  ) : (
                    alertas.map((alerta, i) => {
                      const cfg = ICONO_CONFIG[alerta.icono] ?? ICONO_CONFIG.orden;
                      const leida = new Date(alerta.fecha) <= new Date(ultimaLectura);
                      return (
                        <div key={i} style={{
                          padding: "10px 16px",
                          borderBottom: "1px solid rgba(44,85,69,0.06)",
                          display: "flex", alignItems: "flex-start", gap: 10,
                          backgroundColor: leida ? "white" : "rgba(44,85,69,0.025)",
                        }}>
                          <div style={{
                            width: 32, height: 32, borderRadius: "50%",
                            backgroundColor: cfg.bg, flexShrink: 0,
                            display: "flex", alignItems: "center", justifyContent: "center",
                          }}>
                            {alerta.icono === "orden" && <ShoppingBag size={14} color={cfg.color} />}
                            {alerta.icono === "venta" && <Receipt size={14} color={cfg.color} />}
                            {alerta.icono === "caja" && <span style={{ fontSize: 14 }}>💰</span>}
                          </div>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <p style={{
                              fontFamily: "'Lato', sans-serif", fontSize: 12.5,
                              fontWeight: leida ? 400 : 600,
                              color: "#333", margin: 0, lineHeight: 1.4,
                            }}>
                              {alerta.mensaje}
                            </p>
                            <p style={{
                              fontFamily: "'Lato', sans-serif", fontSize: 11,
                              color: "rgba(44,85,69,0.5)", margin: "2px 0 0 0",
                            }}>
                              {formatHora(alerta.fecha)}
                            </p>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Chip usuario */}
        <div className="flex items-center gap-2 rounded-full px-3 py-1.5"
          style={{ backgroundColor: "#2C5545" }}>
          <div className="rounded-full flex items-center justify-center"
            style={{
              width: 22, height: 22, backgroundColor: "#1E4A37",
              fontFamily: "'Lato', sans-serif", fontSize: 10,
              fontWeight: 700, color: "white",
            }}>
            {initials}
          </div>
          <span style={{ fontFamily: "'Lato', sans-serif", fontSize: 12.5, fontWeight: 500, color: "white" }}>
            {user?.nombre?.split(" ")[0] || "Usuario"}
          </span>
        </div>
      </div>
    </header>
  );
}
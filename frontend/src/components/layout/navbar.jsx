import { useLocation } from "react-router-dom";
import { Bell, Menu } from "lucide-react";
import authService from "../../services/authService";
import { useReloj } from "../../hooks/useReloj";

const PAGE_TITLES = {
  "/dashboard": "Dashboard",
  "/mesas": "Mesas",
  "/ordenes": "Órdenes",
  "/caja": "Caja",
  "/productos": "Productos",
  "/promociones": "Promociones",
  "/insumos": "Insumos",
  "/reportes": "Reportes",
  "/usuarios": "Usuarios",
  "/roles": "Roles y Permisos",
};

export default function Navbar({ onMenuClick }) {
  const location = useLocation();
  const user = authService.getUser();
  const titulo = PAGE_TITLES[location.pathname] || "Memo's Café";
  const initials = user.nombre
    ? user.nombre.split(" ").slice(0, 2).map((n) => n[0]).join("").toUpperCase()
    : "U";

  const ahora = useReloj();
  return (
    <header
      className="flex items-center justify-between px-3 sm:px-5 md:px-8 shrink-0"
      style={{ backgroundColor: "#F8F4EE", borderBottom: "1px solid rgba(44,85,69,0.12)", height: "64px" }}
    >
      <div className="flex items-center gap-2 min-w-0">
        {/* Hamburguesa — solo móvil */}
        <button
          onClick={onMenuClick}
          className="md:hidden rounded-lg flex items-center justify-center shrink-0"
          style={{ width: 36, height: 36, backgroundColor: "rgba(44,85,69,0.08)" }}
        >
          <Menu size={19} strokeWidth={1.8} style={{ color: "#2C5545" }} />
        </button>

        <h1
          className="truncate"
          style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "22px",
            fontWeight: 600,
            color: "#2C5545",
            lineHeight: 1,
            margin: 0,
          }}
        >
          {titulo}
        </h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4 shrink-0">
        {/* Fecha y hora — se oculta en móvil, se compacta en tablet */}
        <div className="text-right hidden sm:block">
          <p
            className="hidden md:block"
            style={{ fontFamily: "'Lato', sans-serif", fontSize: 12.5, color: "#2C5545", fontWeight: 500, margin: 0, textTransform: "capitalize" }}
          >
            {ahora.toLocaleDateString("es-PE", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </p>
          <p style={{ fontFamily: "'Lato', sans-serif", fontSize: 11.5, color: "rgba(44,85,69,0.6)", margin: 0 }}>
            <span className="hidden md:inline">Lima, Perú — </span>
            {ahora.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit", hour12: true })}
          </p>
        </div>

        {/* Campana — se oculta en móvil muy chico */}
        <button
          className="relative rounded-full items-center justify-center hidden xs:flex sm:flex"
          style={{ width: 38, height: 38, backgroundColor: "rgba(44,85,69,0.07)" }}
        >
          <Bell size={17} strokeWidth={1.8} style={{ color: "#2C5545" }} />
          <span className="absolute rounded-full" style={{ width: 7, height: 7, backgroundColor: "#C9A84C", top: 8, right: 8 }} />
        </button>

        {/* Chip del usuario — nombre se oculta en móvil, solo avatar */}
        <div className="flex items-center gap-2 rounded-full px-2 sm:px-3 py-1.5" style={{ backgroundColor: "#2C5545" }}>
          <div
            className="rounded-full flex items-center justify-center shrink-0"
            style={{ width: 22, height: 22, backgroundColor: "#1E4A37", fontFamily: "'Lato', sans-serif", fontSize: 10, fontWeight: 700, color: "white" }}
          >
            {initials}
          </div>
          <span
            className="hidden sm:inline"
            style={{ fontFamily: "'Lato', sans-serif", fontSize: 12.5, fontWeight: 500, color: "white" }}
          >
            {user.nombre?.split(" ")[0] || "Usuario"}
          </span>
        </div>
      </div>
    </header>
  );
}

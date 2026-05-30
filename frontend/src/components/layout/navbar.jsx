import { useLocation } from "react-router-dom";
import { Bell } from "lucide-react";
import authService from "../../services/authService";

// Mapeo de ruta → título de página
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

// Formatea la fecha actual en español: "Viernes, 30 de mayo de 2026"
function getFechaActual() {
  return new Date().toLocaleDateString("es-PE", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

// Formatea la hora actual: "09:42 AM"
function getHoraActual() {
  return new Date().toLocaleTimeString("es-PE", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

export default function Navbar() {
  const location = useLocation();
  const user = authService.getUser();

  // Título dinámico según la ruta actual
  const titulo = PAGE_TITLES[location.pathname] || "Memo's Café";

  // Iniciales para el chip de usuario
  const initials = user.nombre
    ? user.nombre
        .split(" ")
        .slice(0, 2)
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : "U";

  return (
    <header
      className="flex items-center justify-between px-8 shrink-0"
      style={{
        backgroundColor: "#F8F4EE",
        borderBottom: "1px solid rgba(44,85,69,0.12)",
        height: "64px",
      }}
    >
      {/* Título de la página actual */}
      <h1
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

      <div className="flex items-center gap-4">
        {/* Fecha y hora */}
        <div className="text-right">
          <p
            style={{
              fontFamily: "'Lato', sans-serif",
              fontSize: 12.5,
              color: "#2C5545",
              fontWeight: 500,
              margin: 0,
              textTransform: "capitalize",
            }}
          >
            {getFechaActual()}
          </p>
          <p
            style={{
              fontFamily: "'Lato', sans-serif",
              fontSize: 11.5,
              color: "rgba(44,85,69,0.6)",
              margin: 0,
            }}
          >
            Lima, Perú — {getHoraActual()}
          </p>
        </div>

        {/* Campana de notificaciones */}
        <button
          className="relative rounded-full flex items-center justify-center"
          style={{ width: 38, height: 38, backgroundColor: "rgba(44,85,69,0.07)" }}
        >
          <Bell size={17} strokeWidth={1.8} style={{ color: "#2C5545" }} />
          {/* Badge rojo — puedes condicionar esto cuando tengas notificaciones reales */}
          <span
            className="absolute rounded-full"
            style={{ width: 7, height: 7, backgroundColor: "#C9A84C", top: 8, right: 8 }}
          />
        </button>

        {/* Chip del usuario */}
        <div
          className="flex items-center gap-2 rounded-full px-3 py-1.5"
          style={{ backgroundColor: "#2C5545" }}
        >
          <div
            className="rounded-full flex items-center justify-center"
            style={{
              width: 22,
              height: 22,
              backgroundColor: "#1E4A37",
              fontFamily: "'Lato', sans-serif",
              fontSize: 10,
              fontWeight: 700,
              color: "white",
            }}
          >
            {initials}
          </div>
          <span
            style={{
              fontFamily: "'Lato', sans-serif",
              fontSize: 12.5,
              fontWeight: 500,
              color: "white",
            }}
          >
            {user.nombre?.split(" ")[0] || "Usuario"}
          </span>
        </div>
      </div>
    </header>
  );
}
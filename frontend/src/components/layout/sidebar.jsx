import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Table2,
  ClipboardList,
  Receipt,
  Package,
  BarChart3,
  Boxes,
  Users,
  ShieldCheck,
  Tag,
  LogOut,
} from "lucide-react";
import authService from "../../services/authService";

const NAV_ITEMS = [
  {
    icon: LayoutDashboard,
    label: "Dashboard",
    path: "/dashboard",
    roles: null,
  },
  {
    icon: Table2,
    label: "Mesas",
    path: "/mesas",
    roles: null,
  },
  {
    icon: ClipboardList,
    label: "Órdenes",
    path: "/ordenes",
    roles: null,
  },
  {
    icon: Receipt,
    label: "Caja",
    path: "/caja",
    roles: ["admin", "cajero"],
  },
  {
    icon: Package,
    label: "Productos",
    path: "/productos",
    roles: ["admin"],
  },
  {
    icon: Tag,
    label: "Promociones",
    path: "/promociones",
    roles: ["admin"],
  },
  {
    icon: Tag,
    label: "Categorias",
    path: "/categorias",
    roles: ["admin"],
  },
  {
    icon: Boxes,
    label: "Insumos",
    path: "/insumos",
    roles: ["admin"],
  },
  {
    icon: BarChart3,
    label: "Reportes",
    path: "/reportes",
    roles: ["admin"],
  },
  {
    icon: Users,
    label: "Usuarios",
    path: "/usuarios",
    roles: ["admin"],
  },
  {
    icon: ShieldCheck,
    label: "Roles y Permisos",
    path: "/roles",
    roles: ["admin"],
  },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const user = authService.getUser();

  // Filtra los ítems según los roles del usuario
  const visibleItems = NAV_ITEMS.filter(({ roles }) => {
    if (!roles) return true;
    return roles.some((role) => authService.hasRole(role));
  });

  const handleLogout = () => {
    authService.logout();
    navigate("/login");
  };

  // Iniciales del nombre para el avatar
  const initials = user.nombre
    ? user.nombre
        .split(" ")
        .slice(0, 2)
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : "U";

  return (
    <aside
      className="flex flex-col h-full shrink-0"
      style={{ backgroundColor: "#2C5545", width: "220px" }}
    >
      {/* Logo */}
      <div
        className="flex flex-col items-center py-7 px-5 border-b"
        style={{ borderColor: "rgba(255,255,255,0.12)" }}
      >
        <div className="flex items-center gap-2.5">
          {/* Flor SVG — igual al Figma */}
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <circle cx="18" cy="18" r="4" fill="white" opacity="0.9" />
            <ellipse cx="18" cy="8" rx="3.5" ry="5.5" fill="white" opacity="0.85" />
            <ellipse cx="18" cy="28" rx="3.5" ry="5.5" fill="white" opacity="0.85" />
            <ellipse cx="8" cy="18" rx="5.5" ry="3.5" fill="white" opacity="0.85" />
            <ellipse cx="28" cy="18" rx="5.5" ry="3.5" fill="white" opacity="0.85" />
            <ellipse cx="10.5" cy="10.5" rx="3.5" ry="5.5" transform="rotate(-45 10.5 10.5)" fill="white" opacity="0.75" />
            <ellipse cx="25.5" cy="25.5" rx="3.5" ry="5.5" transform="rotate(-45 25.5 25.5)" fill="white" opacity="0.75" />
            <ellipse cx="25.5" cy="10.5" rx="3.5" ry="5.5" transform="rotate(45 25.5 10.5)" fill="white" opacity="0.75" />
            <ellipse cx="10.5" cy="25.5" rx="3.5" ry="5.5" transform="rotate(45 10.5 25.5)" fill="white" opacity="0.75" />
            <circle cx="18" cy="18" r="3" fill="white" />
          </svg>
          <span
            className="text-white tracking-wide"
            style={{
              fontFamily: "'Playfair Display', serif",
              fontSize: "20px",
              fontWeight: 600,
              letterSpacing: "0.04em",
            }}
          >
            Memo's
          </span>
        </div>
        <span
          className="text-white mt-1"
          style={{
            fontFamily: "'Lato', sans-serif",
            fontSize: "10px",
            letterSpacing: "0.18em",
            opacity: 0.6,
            textTransform: "uppercase",
          }}
        >
          Café
        </span>
      </div>

      {/* Navegación */}
      <nav className="flex-1 py-4 px-3 flex flex-col gap-0.5 overflow-y-auto">
        {visibleItems.map(({ icon: Icon, label, path }) => (
          <NavLink
            key={path}
            to={path}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg w-full text-left transition-colors"
            style={({ isActive }) => ({
              backgroundColor: isActive ? "#1E4A37" : "transparent",
              color: "white",
              fontFamily: "'Lato', sans-serif",
              fontSize: "13.5px",
              fontWeight: isActive ? 500 : 400,
              opacity: isActive ? 1 : 0.82,
              textDecoration: "none",
            })}
          >
            <Icon size={17} strokeWidth={1.8} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Usuario + Logout */}
      <div
        className="px-4 py-5 border-t"
        style={{ borderColor: "rgba(255,255,255,0.12)" }}
      >
        <div className="flex items-center gap-2.5 mb-3">
          <div
            className="rounded-full flex items-center justify-center text-white shrink-0"
            style={{
              width: 34,
              height: 34,
              backgroundColor: "#1E4A37",
              fontFamily: "'Lato', sans-serif",
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            {initials}
          </div>
          <div className="min-w-0">
            <p
              className="text-white truncate"
              style={{ fontFamily: "'Lato', sans-serif", fontSize: 12.5, fontWeight: 500 }}
            >
              {user.nombre || user.email}
            </p>
            <p
              className="truncate"
              style={{ fontFamily: "'Lato', sans-serif", fontSize: 11, color: "rgba(255,255,255,0.55)" }}
            >
              {user.roles?.[0] || "Usuario"}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full rounded-lg px-3 py-2 transition-colors"
          style={{
            backgroundColor: "rgba(255,255,255,0.08)",
            color: "rgba(255,255,255,0.75)",
            fontFamily: "'Lato', sans-serif",
            fontSize: 12.5,
          }}
        >
          <LogOut size={14} strokeWidth={1.8} />
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
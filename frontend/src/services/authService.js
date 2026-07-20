import api from "./api";

/**
 * Decodifica el payload de un JWT sin librería externa.
 * El JWT tiene 3 partes separadas por puntos: header.payload.signature
 * Solo necesitamos el payload (índice 1).
 */
const decodeToken = (token) => {
  try {
    const payload = token.split(".")[1];
    // atob decodifica base64 — el payload del JWT está en base64url
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
  } catch {
    return null;
  }
};

const authService = {
  login: async (email, password) => {
    const response = await api.post("/auth/login/", { email, password });
    const { access, refresh } = response.data;

    // Guarda los tokens
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);

    // Decodifica el payload y guarda los datos del usuario
    const payload = decodeToken(access);
    let roles = [];
    if (payload) {
      roles = payload.roles || [];
      localStorage.setItem("user_roles", JSON.stringify(roles));
      localStorage.setItem("user_email", payload.email || "");
      localStorage.setItem("user_nombre", payload.nombre || payload.email || "");
      localStorage.setItem("user_id", payload.user_id || "");
    }

    // Cachea que módulos puede ver este usuario (PermisoRol), para que
    // Sidebar/PrivateRoute decidan sin pegarle al backend en cada render.
    // Si falla, queda sin módulos extra hasta el próximo login — admin
    // igual tiene acceso total vía bypass en el backend y en tieneModulo.
    try {
      const { data } = await api.get("/roles/permisos/");
      const permisos = Array.isArray(data) ? data : (data.results ?? []);
      const modulosPermitidos = permisos
        .filter((p) => roles.includes(p.rol) && p.puede_acceder)
        .map((p) => p.modulo);
      localStorage.setItem("user_modulos", JSON.stringify([...new Set(modulosPermitidos)]));
    } catch {
      localStorage.setItem("user_modulos", JSON.stringify([]));
    }

    return response.data;
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_roles");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_nombre");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_modulos");
    window.location.href = "/login";
  },


  isAuthenticated: () => {
    const token = localStorage.getItem("access_token");
    if (!token) return false;
    const payload = decodeToken(token);
    if (!payload) return false;
    // exp está en segundos, Date.now() en milisegundos
    return payload.exp * 1000 > Date.now();
  },

  getUser: () => ({
    id: localStorage.getItem("user_id") || "",
    email: localStorage.getItem("user_email") || "",
    nombre: localStorage.getItem("user_nombre") || "",
    roles: JSON.parse(localStorage.getItem("user_roles") || "[]"),
  }),

  hasRole: (role) => {
    const roles = JSON.parse(localStorage.getItem("user_roles") || "[]");
    return roles.includes(role);
  },

  // Admin siempre tiene acceso a todo, sin importar los toggles de
  // PermisoRol — evita que un admin se bloquee a sí mismo. Mismo criterio
  // que el backend (memos_cafe.utils.permissions.ModuloHabilitado).
  tieneModulo: (modulo) => {
    const roles = JSON.parse(localStorage.getItem("user_roles") || "[]");
    if (roles.includes("admin")) return true;
    const modulos = JSON.parse(localStorage.getItem("user_modulos") || "[]");
    return modulos.includes(modulo);
  },
};

export default authService;
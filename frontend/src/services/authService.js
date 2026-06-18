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
    if (payload) {
      localStorage.setItem("user_roles", JSON.stringify(payload.roles || []));
      localStorage.setItem("user_email", payload.email || "");
      localStorage.setItem("user_nombre", payload.nombre || payload.email || "");
      localStorage.setItem("user_id", payload.user_id || "");
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
};

export default authService;
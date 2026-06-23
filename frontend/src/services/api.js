import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Request interceptor — agrega JWT ─────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor — manejo global de errores ──────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // 401 — token expirado, intenta refrescar
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");
        const { data } = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });
        localStorage.setItem("access_token", data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return api(originalRequest);
      } catch {
        // Refresh falló — sesión expirada
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    // 403 — sin permisos
    if (status === 403) {
      window.dispatchEvent(new CustomEvent("api:forbidden"));
    }

    // 500 — error del servidor
    if (status >= 500) {
      window.dispatchEvent(new CustomEvent("api:server-error"));
    }

    // Sin conexión
    if (!error.response) {
      window.dispatchEvent(new CustomEvent("api:network-error"));
    }

    return Promise.reject(error);
  }
);

export default api;

import api from "./api";

const authService = {
  login: async (email, password) => {
    const response = await api.post("/auth/login/", { email, password });
    const { access, refresh } = response.data;
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  },

  isAuthenticated: () => {
    return !!localStorage.getItem("access_token");
  },
};

export default authService;
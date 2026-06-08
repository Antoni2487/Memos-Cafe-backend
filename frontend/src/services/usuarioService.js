import api from "./api";

const usuarioService = {
  getAll:       ()         => api.get("/users/"),
  getById:      (pk)       => api.get(`/users/${pk}/`),
  create:       (data)     => api.post("/users/", data),
  update:       (pk, data) => api.patch(`/users/${pk}/`, data),
  delete:       (pk)       => api.delete(`/users/${pk}/`),
  toggleActivo: (pk)       => api.post(`/users/${pk}/toggle-activo/`),
  getMe:        ()         => api.get("/users/me/"),
};

export default usuarioService;

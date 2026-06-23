import api from "./api";

const promocionService = {
  getAll:     ()         => api.get("/productos/promociones/"),
  getById:    (id)       => api.get(`/productos/promociones/${id}/`),
  crear:      (data)     => api.post("/productos/promociones/crear/", data),
  editar:     (id, data) => api.patch(`/productos/promociones/${id}/editar/`, data),
  activar:    (id)       => api.post(`/productos/promociones/${id}/activar/`),
  desactivar: (id)       => api.post(`/productos/promociones/${id}/desactivar/`),
};

export default promocionService;
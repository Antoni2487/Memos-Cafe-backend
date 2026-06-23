import api from "./api";

const mesasService = {
  listar:        ()              => api.get("/mesas/"),
  crear:         (data)          => api.post("/mesas/", data),
  editar:        (id, data)      => api.put(`/mesas/${id}/`, data),
  darDeBaja:     (id)            => api.delete(`/mesas/${id}/`),
  cambiarEstado: (id, estado)    => api.patch(`/mesas/${id}/estado/`, { estado }),
};

export default mesasService;
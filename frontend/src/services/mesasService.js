import api from "./api";

const mesasService = {
  listar:        ()              => api.get("/mesas/"),
  cambiarEstado: (id, estado)    => api.patch(`/mesas/${id}/estado/`, { estado }),
};

export default mesasService;

import api from "./api";

const ordenesService = {
  listar:          ()                    => api.get("/ordenes/"),
  crear:           (payload)             => api.post("/ordenes/crear/", payload),
  agregarDetalle:  (ordenId, payload)    => api.post(`/ordenes/${ordenId}/detalles/`, payload),
  eliminarDetalle: (ordenId, detalleId)  => api.delete(`/ordenes/${ordenId}/detalles/${detalleId}/`),
  marcarImpreso:   (ordenId, detalleIds) => api.post(`/ordenes/${ordenId}/marcar-impreso/`, { detalle_ids: detalleIds }),
  anular:          (ordenId)             => api.post(`/ordenes/${ordenId}/anular/`),
};

export default ordenesService;

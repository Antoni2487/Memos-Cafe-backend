import api from "./api";

const productoService = {
  listar: () => api.get("/productos/"),
  listarPromociones: () => api.get("/productos/promociones/"),
  crear: (data) => api.post("/productos/crear/", toFormData(data)),
  editar: (id, data) => api.patch(`/productos/${id}/editar/`, toFormData(data)),
  activar: (id) => api.post(`/productos/${id}/activar/`),
  desactivar: (id) => api.post(`/productos/${id}/desactivar/`),
};

/**
 * Convierte el objeto plano del formulario a FormData.
 * No se fija Content-Type manualmente: axios lo detecta solo al ver una
 * instancia de FormData y agrega el boundary correcto automaticamente.
 * Fijarlo a mano rompe el request (falta el boundary).
 */
function toFormData(data) {
  const fd = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (key === "imagen") {
      if (value instanceof File) fd.append("imagen", value);
      return;
    }
    if (value !== undefined && value !== null) fd.append(key, value);
  });
  return fd;
}

export default productoService;

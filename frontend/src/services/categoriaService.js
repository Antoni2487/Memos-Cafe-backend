import api from "./api";

const categoriaService = {
  listar:     ()             => api.get("/productos/categorias/"),
  crear:      (nombre)       => api.post("/productos/categorias/crear/", { nombre }),
  editar:     (id, nombre)   => api.patch(`/productos/categorias/${id}/editar/`, { nombre }),
  activar:    (id)           => api.post(`/productos/categorias/${id}/activar/`),
  desactivar: (id)           => api.post(`/productos/categorias/${id}/desactivar/`),
};

export default categoriaService;

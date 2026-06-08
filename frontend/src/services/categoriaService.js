import api from "./api";

const categoriaService = {
  listar:     ()       => api.get("/productos/categorias/"),
  crear:      (nombre) => api.post("/productos/categorias/crear/", { nombre }),
  desactivar: (id)     => api.post(`/productos/categorias/${id}/desactivar/`),
};

export default categoriaService;

import api from "./api";

const productosService = {
  listar:            ()  => api.get("/productos/"),
  listarPromociones: ()  => api.get("/productos/promociones/"),
};

export default productosService;

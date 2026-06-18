import api from "./api";

const homeService = {
  getMesas:   () => api.get("/mesas/"),
  getOrdenes: () => api.get("/ordenes/"),
};

export default homeService;

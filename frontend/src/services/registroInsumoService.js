import api from "./api";

const registroInsumoService = {
    listar: (params) => api.get("/insumos/registros/", { params }),
    registrar: (data) => api.post("/insumos/registros/registrar/", data),
};

export default registroInsumoService;
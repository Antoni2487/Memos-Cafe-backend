import api from "./api";

const insumoService = {
    listar: (params) => api.get("/insumos/", { params }),
    crear: (data) => api.post("/insumos/crear/", data),
    editar: (id, data) => api.patch(`/insumos/${id}/editar/`, data),
    activar: (id) => api.post(`/insumos/${id}/activar/`),
    desactivar: (id) => api.post(`/insumos/${id}/desactivar/`),
};

export default insumoService;
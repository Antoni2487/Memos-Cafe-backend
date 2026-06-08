import api from "./api";

const ordenesService = {
  // GET /api/ordenes/ — obtiene lista de órdenes abiertas
  getOrdenes: async () => {
    const response = await api.get("/ordenes/");
    return response.data;
  },

  // POST /api/ordenes/crear/ — crea una nueva orden con ítems
  crearOrden: async (tipoOrden, mesaId, detalles) => {
    const data = {
      tipo_orden: tipoOrden,
      mesa: tipoOrden === "mesa" ? mesaId : null,
      detalles: detalles.map((item) => ({
        producto: item.producto_id || null,
        promocion: item.promocion_id || null,
        cantidad: item.cantidad,
        nota: item.nota || "",
      })),
    };
    const response = await api.post("/ordenes/crear/", data);
    return response.data;
  },

  // POST /api/ordenes/{id}/detalles/ — agrega un ítem a una orden existente
  agregarDetalle: async (ordenId, producto, promocion, cantidad, nota = "") => {
    const data = {
      producto: producto || null,
      promocion: promocion || null,
      cantidad,
      nota,
    };
    const response = await api.post(`/ordenes/${ordenId}/detalles/`, data);
    return response.data;
  },

  // DELETE /api/ordenes/{id}/detalles/{detalleId}/ — elimina un ítem de una orden
  eliminarDetalle: async (ordenId, detalleId) => {
    const response = await api.delete(
      `/ordenes/${ordenId}/detalles/${detalleId}/`
    );
    return response.data;
  },

  // POST /api/ordenes/{id}/anular/ — anula una orden (solo admin)
  anularOrden: async (ordenId) => {
    const response = await api.post(`/ordenes/${ordenId}/anular/`);
    return response.data;
  },
};

export default ordenesService;

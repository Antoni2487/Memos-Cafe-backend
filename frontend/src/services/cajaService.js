import api from "./api";

const cajaService = {
    // Sesión
    obtenerEstado: () => api.get("/caja/sesiones/estado/"),
    abrirSesion: (datos) => api.post("/caja/sesiones/abrir/", datos),
    cerrarSesion: (datos) => api.post("/caja/sesiones/cerrar/", datos),

    // Movimientos
    listarMovimientos: () => api.get("/caja/movimientos/"),
    registrarMovimiento: (datos) => api.post("/caja/movimientos/", datos),

    // Pagos
    listarPagos: () => api.get("/caja/pagos/"),
    procesarPago: (datos) => api.post("/caja/pagos/procesar/", datos),
    anularPago: (id) => api.post(`/caja/pagos/${id}/anular/`),

    // Comprobantes
    emitirComprobante: (datos) => api.post("/caja/comprobantes/emitir/", datos),
};

export default cajaService;
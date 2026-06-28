import api from "./api";

const reporteService = {
  // Reporte de ventas por rango de fechas
  getVentas: (params) =>
    api.get("/reportes/ventas/", { params }),

  // Reporte de productos más vendidos
  getProductos: (params) =>
    api.get("/reportes/productos/", { params }),

  // Reporte de caja por turno o rango de fechas
  getCaja: (params) =>
    api.get("/reportes/caja/", { params }),

  // Exportar ventas a Excel — descarga directa
  exportarVentas: (params) =>
    api.get("/reportes/ventas/export/", {
      params,
      responseType: "blob",
    }),

  // Exportar caja a Excel — descarga directa
  exportarCaja: (params) =>
    api.get("/reportes/caja/export/", {
      params,
      responseType: "blob",
    }),

  // Exportar productos a Excel — descarga directa
  exportarProductos: (params) =>
    api.get("/reportes/productos/export/", {
      params,
      responseType: "blob",
    }),
};

// Utilidad para disparar la descarga del blob en el navegador
export function descargarBlob(blob, nombreArchivo) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombreArchivo;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export default reporteService;
import { useState, useEffect, useCallback } from "react";
import ordenesService from "../services/ordenesService";

export function useOrdenes() {
  const [ordenes, setOrdenes]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const cargar = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await ordenesService.listar();
      setOrdenes(Array.isArray(data) ? data : (data.results ?? []));
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar órdenes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const crear = useCallback(async (payload) => {
    const { data } = await ordenesService.crear(payload);
    setOrdenes((prev) => [data, ...prev]);
    return data;
  }, []);

  const anular = useCallback(async (ordenId) => {
    const { data } = await ordenesService.anular(ordenId);
    setOrdenes((prev) => prev.map((o) => (o.id === data.id ? data : o)));
    return data;
  }, []);

  const eliminarDetalle = useCallback(async (ordenId, detalleId) => {
    const { data } = await ordenesService.eliminarDetalle(ordenId, detalleId);
    setOrdenes((prev) => prev.map((o) => (o.id === data.id ? data : o)));
    return data;
  }, []);

  const marcarImpreso = useCallback(async (ordenId, detalleIds) => {
    const { data } = await ordenesService.marcarImpreso(ordenId, detalleIds);
    setOrdenes((prev) => prev.map((o) => (o.id === data.id ? data : o)));
    return data;
  }, []);

  const ordenesAbiertas  = ordenes.filter((o) => o.estado === "abierta");
  const ordenesCerradas  = ordenes.filter((o) => o.estado === "cerrada");
  const ordenesAnuladas  = ordenes.filter((o) => o.estado === "anulada");

  return {
    ordenes,
    ordenesAbiertas,
    ordenesCerradas,
    ordenesAnuladas,
    loading,
    error,
    cargar,
    crear,
    anular,
    eliminarDetalle,
    marcarImpreso,
  };
}

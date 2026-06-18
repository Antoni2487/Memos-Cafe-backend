import { useState, useEffect, useCallback } from "react";
import homeService from "../services/homeService";

export default function useHome() {
  const [mesas, setMesas]     = useState([]);
  const [ordenes, setOrdenes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError]     = useState(null);

  const cargar = useCallback(async () => {
    try {
      setCargando(true);
      setError(null);
      const [resMesas, resOrdenes] = await Promise.all([
        homeService.getMesas(),
        homeService.getOrdenes(),
      ]);
      setMesas(resMesas.data.results ?? resMesas.data);
      setOrdenes(resOrdenes.data.results ?? resOrdenes.data);
    } catch {
      setError("Error al cargar la información.");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const mesasLibres   = mesas.filter((m) => m.estado === "libre").length;
  const mesasOcupadas = mesas.filter((m) => m.estado === "ocupada").length;
  const ordenesAbiertas = ordenes.filter((o) => o.estado === "abierta").length;

  return {
    mesas, ordenes,
    mesasLibres, mesasOcupadas, ordenesAbiertas,
    totalMesas: mesas.length,
    cargando, error, cargar,
  };
}

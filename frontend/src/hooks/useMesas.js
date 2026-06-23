import { useState, useEffect, useCallback } from "react";
import mesasService from "../services/mesasService";

export default function useMesas() {
  const [mesas, setMesas]     = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError]     = useState(null);

  const cargar = useCallback(async () => {
    try {
      setCargando(true);
      setError(null);
      const { data } = await mesasService.listar();
      const lista = data.results ?? data;
      setMesas(lista);
    } catch {
      setError("Error al cargar mesas");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  return { mesas, cargando, error, recargar: cargar };
}
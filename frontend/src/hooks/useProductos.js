import { useState, useEffect, useCallback } from "react";
import productoService from "../services/productoService";

export default function useProductos() {
  const [productos, setProductos] = useState([]);
  const [cargando, setCargando]   = useState(true);
  const [error, setError]         = useState(null);

  const cargar = useCallback(async () => {
    try {
      setCargando(true);
      setError(null);
      const { data } = await productoService.listar();
      const lista = (data.results ?? data).sort((a, b) => a.id - b.id);
      setProductos(lista);
    } catch {
      setError("Error al cargar productos");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  return { productos, cargando, error, recargar: cargar };
}

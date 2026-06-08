import { useState, useEffect, useCallback, useMemo } from "react";
import categoriaService from "../services/categoriaService";

export function useCategorias() {
  const [categorias, setCategorias]       = useState([]);
  const [loading, setLoading]             = useState(true);
  const [error, setError]                 = useState(null);
  const [search, setSearch]               = useState("");
  const [showModal, setShowModal]         = useState(false);
  const [confirmTarget, setConfirmTarget] = useState(null);
  const [deactivating, setDeactivating]   = useState(false);
  const [deactivateError, setDeactivateError] = useState(null);

  const cargar = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await categoriaService.listar();
      setCategorias(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar categorías");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return q ? categorias.filter((c) => c.nombre.toLowerCase().includes(q)) : categorias;
  }, [categorias, search]);

  const handleCreated = useCallback(async (nombre) => {
    const { data } = await categoriaService.crear(nombre);
    setCategorias((prev) => [data, ...prev]);
    setShowModal(false);
  }, []);

  const pedirConfirmacion = useCallback((cat) => {
    setDeactivateError(null);
    setConfirmTarget(cat);
  }, []);

  const confirmarDesactivar = useCallback(async () => {
    if (!confirmTarget) return;
    setDeactivating(true);
    setDeactivateError(null);
    try {
      const { data } = await categoriaService.desactivar(confirmTarget.id);
      setCategorias((prev) => prev.map((c) => (c.id === data.id ? data : c)));
      setConfirmTarget(null);
    } catch (err) {
      setDeactivateError(err.response?.data?.detail || "Error al desactivar");
    } finally {
      setDeactivating(false);
    }
  }, [confirmTarget]);

  const cancelarConfirm = useCallback(() => {
    setConfirmTarget(null);
    setDeactivateError(null);
  }, []);

  return {
    // datos
    categorias,
    filtered,
    loading,
    error,
    // búsqueda
    search,
    setSearch,
    // modal crear
    showModal,
    setShowModal,
    // desactivar
    confirmTarget,
    deactivating,
    deactivateError,
    // acciones
    cargar,
    handleCreated,
    pedirConfirmacion,
    confirmarDesactivar,
    cancelarConfirm,
  };
}

import { useState, useEffect, useCallback } from "react";
import rolesService from "../services/rolesService";

export default function useRoles() {
  const [permisos, setPermisos]   = useState([]);
  const [cargando, setCargando]   = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError]         = useState(null);
  const [exito, setExito]         = useState(false);

  const cargar = useCallback(async () => {
    try {
      setCargando(true);
      const { data } = await rolesService.getAll();
      const lista = data.results ?? data;
      setPermisos(lista);
    } catch {
      setError("Error al cargar los permisos.");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const handleToggle = async (permiso) => {
    // Optimistic update — actualiza UI antes de la respuesta
    setPermisos((prev) =>
      prev.map((p) =>
        p.id === permiso.id ? { ...p, puede_acceder: !p.puede_acceder } : p
      )
    );

    try {
      setGuardando(true);
      setError(null);
      await rolesService.update(permiso.id, { puede_acceder: !permiso.puede_acceder });
      setExito(true);
      setTimeout(() => setExito(false), 2000);
    } catch {
      // Revierte si falla
      setPermisos((prev) =>
        prev.map((p) =>
          p.id === permiso.id ? { ...p, puede_acceder: permiso.puede_acceder } : p
        )
      );
      setError("Error al actualizar el permiso.");
    } finally {
      setGuardando(false);
    }
  };

  // Agrupa permisos por módulo para la tabla
  const porModulo = permisos.reduce((acc, p) => {
    if (!acc[p.modulo]) {
      acc[p.modulo] = { modulo: p.modulo, label: p.modulo_label, roles: {} };
    }
    acc[p.modulo].roles[p.rol] = p;
    return acc;
  }, {});

  return {
    porModulo,
    cargando,
    guardando,
    error,
    exito,
    setError,
    handleToggle,
  };
}

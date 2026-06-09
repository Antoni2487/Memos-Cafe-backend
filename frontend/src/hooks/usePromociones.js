import { useState, useEffect, useCallback } from "react";
import promocionService from "../services/promocionService";

export default function usePromociones() {
    const [promociones, setPromociones] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);

    const cargar = useCallback(async () => {
        try {
            setCargando(true);
            setError(null);
            const { data } = await promocionService.getAll();
            const lista = (data.results ?? data).sort((a, b) => a.id - b.id);
            setPromociones(lista);
        } catch {
            setError("Error al cargar promociones");
        } finally {
            setCargando(false);
        }
    }, []);

    useEffect(() => { cargar(); }, [cargar]);

    return { promociones, cargando, error, recargar: cargar };
}
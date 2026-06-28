import { useState, useEffect, useCallback } from "react";
import insumoService from "../services/insumoService";

export default function useInsumos() {
    const [insumos, setInsumos] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);

    const cargar = useCallback(async () => {
        try {
            setCargando(true);
            setError(null);
            const { data } = await insumoService.listar();
            const lista = (data.results ?? data).sort((a, b) => a.id - b.id);
            setInsumos(lista);
        } catch {
            setError("Error al cargar insumos");
        } finally {
            setCargando(false);
        }
    }, []);

    useEffect(() => { cargar(); }, [cargar]);

    return { insumos, cargando, error, recargar: cargar };
}
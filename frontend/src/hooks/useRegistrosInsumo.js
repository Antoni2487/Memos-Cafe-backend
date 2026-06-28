import { useState, useEffect, useCallback } from "react";
import registroInsumoService from "../services/registroInsumoService";

export default function useRegistrosInsumo() {
    const [registros, setRegistros] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);

    const cargar = useCallback(async () => {
        try {
            setCargando(true);
            setError(null);
            const { data } = await registroInsumoService.listar();
            setRegistros(data.results ?? data);
        } catch {
            setError("Error al cargar el historial de gastos");
        } finally {
            setCargando(false);
        }
    }, []);

    useEffect(() => { cargar(); }, [cargar]);

    const totalGastado = registros.reduce((acc, r) => acc + Number(r.costo_total), 0);

    const inicioMes = new Date();
    inicioMes.setDate(1);
    inicioMes.setHours(0, 0, 0, 0);
    const gastadoEsteMes = registros
        .filter((r) => new Date(r.fecha) >= inicioMes)
        .reduce((acc, r) => acc + Number(r.costo_total), 0);

    return { registros, cargando, error, recargar: cargar, totalGastado, gastadoEsteMes };
}
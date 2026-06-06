import { useState, useEffect, useCallback } from "react";
import usuarioService from "../services/usuarioService";

const POR_PAGINA = 10;

export default function useUsuarios() {
  const [usuarios, setUsuarios]       = useState([]);
  const [filtrados, setFiltrados]     = useState([]);
  const [cargando, setCargando]       = useState(true);
  const [guardando, setGuardando]     = useState(false);
  const [eliminando, setEliminando]   = useState(false);
  const [togglando, setTogglando]     = useState(false);
  const [pagina, setPagina]           = useState(1);
  const [showForm, setShowForm]       = useState(false);
  const [usuarioEditar, setUsuarioEditar]   = useState(null);
  const [usuarioEliminar, setUsuarioEliminar] = useState(null);
  const [usuarioToggle, setUsuarioToggle]   = useState(null);

  const cargar = useCallback(async () => {
    try {
      setCargando(true);
      const { data } = await usuarioService.getAll();
      const lista = data.results ?? data;
      setUsuarios(lista);
      setFiltrados(lista);
      setPagina(1);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const handleBuscar = useCallback((texto) => {
    const t = texto.toLowerCase();
    setFiltrados(
      usuarios.filter((u) =>
        u.email.toLowerCase().includes(t) ||
        (u.name || "").toLowerCase().includes(t)
      )
    );
    setPagina(1);
  }, [usuarios]);

  const handleGuardar = async (datos) => {
    try {
      setGuardando(true);
      usuarioEditar
        ? await usuarioService.update(usuarioEditar.id, datos)
        : await usuarioService.create(datos);
      setShowForm(false);
      setUsuarioEditar(null);
      await cargar();
    } finally {
      setGuardando(false);
    }
  };

  const handleEliminar = async () => {
    try {
      setEliminando(true);
      await usuarioService.delete(usuarioEliminar.id);
      setUsuarioEliminar(null);
      await cargar();
    } finally {
      setEliminando(false);
    }
  };

  const handleToggleActivo = async () => {
    try {
      setTogglando(true);
      await usuarioService.toggleActivo(usuarioToggle.id);
      setUsuarioToggle(null);
      await cargar();
    } finally {
      setTogglando(false);
    }
  };

  const abrirEditar = (u) => { setUsuarioEditar(u); setShowForm(true); };
  const abrirNuevo  = ()  => { setUsuarioEditar(null); setShowForm(true); };

  const paginados = filtrados.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);

  return {
    // datos
    paginados,
    filtrados,
    cargando,
    guardando,
    eliminando,
    togglando,
    pagina,
    setPagina,
    POR_PAGINA,
    // modales
    showForm,
    usuarioEditar,
    usuarioEliminar,
    usuarioToggle,
    setUsuarioEliminar,
    setUsuarioToggle,
    // acciones
    handleBuscar,
    handleGuardar,
    handleEliminar,
    handleToggleActivo,
    abrirEditar,
    abrirNuevo,
    cerrarForm: () => { setShowForm(false); setUsuarioEditar(null); },
  };
}

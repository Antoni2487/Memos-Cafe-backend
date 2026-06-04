import { useEffect, useState } from "react";
import usuarioService from "../../services/usuarioService";
import UsuarioForm from "../../components/usuarios/UsuarioForm";
// import para libreria de iconos
import { Pencil, Trash2 } from "lucide-react";
import {
  PageHeader,
  DataTable,
  StatusBadge,
  SearchBar,
  ConfirmDialog,
} from "../../components/common";

const POR_PAGINA = 10;

export default function UsuariosPage() {
  const [usuarios, setUsuarios] = useState([]);
  const [filtrados, setFiltrados] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [eliminando, setEliminando] = useState(false);
  const [pagina, setPagina] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [usuarioEditar, setUsuarioEditar] = useState(null);
  const [usuarioEliminar, setUsuarioEliminar] = useState(null);

  const cargar = async () => {
    try {
      setCargando(true);
      const { data } = await usuarioService.getAll();
      // El backend devuelve { count, results, next, previous }
      const lista = data.results ?? data;
      setUsuarios(lista);
      setFiltrados(lista);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => { cargar(); }, []);

  const handleBuscar = (texto) => {
    const t = texto.toLowerCase();
    setFiltrados(
      usuarios.filter((u) =>
        u.email.toLowerCase().includes(t) ||
        (u.name || "").toLowerCase().includes(t)
      )
    );
    setPagina(1);
  };

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

  const abrirEditar = (u) => { setUsuarioEditar(u); setShowForm(true); };
  const abrirNuevo = () => { setUsuarioEditar(null); setShowForm(true); };

  const paginados = filtrados.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);

  const columnas = [
    {
      label: "Usuario",
      key: "name",
      render: (u) => (
        <div className="flex items-center gap-2.5">
          <div style={{
            width: 32, height: 32, borderRadius: "50%",
            backgroundColor: "rgba(44,85,69,0.12)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'Lato', sans-serif", fontSize: 11,
            fontWeight: 700, color: "#2C5545", flexShrink: 0,
          }}>
            {(u.name || u.email).charAt(0).toUpperCase()}
          </div>
          <div>
            <p style={{ margin: 0, fontFamily: "'Lato', sans-serif", fontSize: 13.5, fontWeight: 500, color: "#2C5545" }}>
              {u.name || "—"}
            </p>
            <p style={{ margin: 0, fontFamily: "'Lato', sans-serif", fontSize: 11.5, color: "rgba(44,85,69,0.55)" }}>
              {u.email}
            </p>
          </div>
        </div>
      ),
    },
    {
      label: "Rol",
      key: "groups",
      width: "120px",
      render: (u) => {
        const rol = u.groups?.[0]?.name ?? "Sin rol";
        const colores = {
          admin: { bg: "rgba(44,85,69,0.12)", color: "#2C5545" },
          cajero: { bg: "rgba(201,168,76,0.15)", color: "#9a7a1a" },
          mozo: { bg: "rgba(33,150,243,0.12)", color: "#1565c0" },
        };
        const c = colores[rol.toLowerCase()] ?? { bg: "rgba(120,120,120,0.1)", color: "#666" };
        return (
          <span style={{
            display: "inline-flex", alignItems: "center",
            backgroundColor: c.bg, color: c.color,
            borderRadius: "999px",
            fontFamily: "'Lato', sans-serif",
            fontSize: "11px", fontWeight: 700,
            padding: "3px 10px", letterSpacing: "0.04em",
            textTransform: "capitalize",
          }}>
            {rol}
          </span>
        );
      },
    },
    {
      label: "Estado",
      key: "is_active",
      width: "100px",
      render: (u) => <StatusBadge estado={u.is_active ? "activo" : "inactivo"} />,
    },
    {
      label: "Registro",
      key: "date_joined",
      width: "120px",
      render: (u) => u.date_joined
        ? new Date(u.date_joined).toLocaleDateString("es-PE", { day: "2-digit", month: "short", year: "numeric" })
        : "—",
    },
    {
      label: "Acciones",
      width: "90px",
      render: (u) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => abrirEditar(u)}
            title="Editar"
            style={{
              width: 30, height: 30, borderRadius: "6px",
              border: "1px solid rgba(44,85,69,0.2)",
              backgroundColor: "white", cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#2C5545", transition: "all 0.15s",
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "rgba(44,85,69,0.08)"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "white"}
          >
            <Pencil size={13} strokeWidth={2} />
          </button>
          <button
            onClick={() => setUsuarioEliminar(u)}
            title="Eliminar"
            style={{
              width: 30, height: 30, borderRadius: "6px",
              border: "1px solid rgba(198,40,40,0.2)",
              backgroundColor: "white", cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#c62828", transition: "all 0.15s",
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "rgba(198,40,40,0.06)"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "white"}
          >
            <Trash2 size={13} strokeWidth={2} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        titulo="Gestión de Usuarios"
        descripcion="Administra los accesos y roles del sistema"
        accion={
          <button
            onClick={abrirNuevo}
            style={{
              backgroundColor: "#2C5545", color: "white",
              border: "none", borderRadius: "8px",
              padding: "9px 16px",
              fontFamily: "'Lato', sans-serif",
              fontSize: "13px", fontWeight: 600,
              cursor: "pointer",
            }}
          >
            + Nuevo Usuario
          </button>
        }
      />

      {/* Buscador */}
      <div className="mb-4">
        <SearchBar
          placeholder="Buscar por nombre o email..."
          onBuscar={handleBuscar}
        />
      </div>

      {/* Tabla */}
      <DataTable
        columnas={columnas}
        datos={paginados}
        total={filtrados.length}
        pagina={pagina}
        onPagina={setPagina}
        porPagina={POR_PAGINA}
        cargando={cargando}
        textoVacio="No hay usuarios registrados"
      />

      {/* Formulario */}
      <UsuarioForm
        abierto={showForm}
        usuario={usuarioEditar}
        onGuardar={handleGuardar}
        onCerrar={() => { setShowForm(false); setUsuarioEditar(null); }}
        cargando={guardando}
      />

      {/* Confirmar eliminar */}
      <ConfirmDialog
        abierto={!!usuarioEliminar}
        titulo="¿Eliminar usuario?"
        descripcion={`Estás a punto de eliminar a ${usuarioEliminar?.email}.\nEsta acción no se puede deshacer.`}
        textoOk="Sí, eliminar"
        variante="danger"
        cargando={eliminando}
        onConfirmar={handleEliminar}
        onCancelar={() => setUsuarioEliminar(null)}
      />
    </>
  );
}
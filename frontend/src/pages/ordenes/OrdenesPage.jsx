import { useState, useEffect, useRef } from "react";
import PageHeader from "../../components/common/PageHeader";
import { FormModal } from "../../components/common/Modals";
import { LoadingSpinner, EmptyState } from "../../components/common/LoadingSpinner-EmptyState";
import DataTable from "../../components/common/DataTable";
import StatusBadge from "../../components/common/StatusBadge";
import OrdenForm from "../../components/ordenes/OrdenForm";
import ordenesService from "../../services/ordenesService";
import mesasService from "../../services/mesasService";
import productosService from "../../services/productosService";

export default function OrdenesPage() {
  const [ordenes, setOrdenes]         = useState([]);
  const [mesas, setMesas]             = useState([]);
  const [productos, setProductos]     = useState([]);
  const [promociones, setPromociones] = useState([]);
  const [cargando, setCargando]       = useState(true);
  const [cargandoForm, setCargandoForm] = useState(false);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [error, setError]             = useState("");
  const submitRef = useRef(null);

  const cargarOrdenes = async () => {
    try {
      setError("");
      const { data } = await ordenesService.listar();
      setOrdenes(data.results ?? data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar órdenes");
    }
  };

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");
      const [resOrdenes, resMesas, resProd, resPromo] = await Promise.all([
        ordenesService.listar(),
        mesasService.listar(),
        productosService.listar(),
        productosService.listarPromociones(),
      ]);
      setOrdenes(resOrdenes.data.results   ?? resOrdenes.data);
      setMesas(resMesas.data.results       ?? resMesas.data);
      setProductos(resProd.data.results    ?? resProd.data);
      setPromociones(resPromo.data.results ?? resPromo.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar datos");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
    const intervalo = setInterval(cargarOrdenes, 5000);
    return () => clearInterval(intervalo);
  }, []);

  const manejarGuardar = async () => {
    if (!submitRef.current) return;
    setCargandoForm(true);
    setError("");
    try {
      await submitRef.current();
      setModalAbierto(false);
      cargarDatos();
    } catch (err) {
      setError(err.response?.data?.detail || "Error al crear orden");
    } finally {
      setCargandoForm(false);
    }
  };

  const manejarCrearOrden = async (payload) => {
    const { data } = await ordenesService.crear(payload);
    setOrdenes((prev) => [data, ...prev]);
  };

  if (cargando) return <LoadingSpinner />;

  const columnas = [
    { label: "ID",       width: "60px" },
    { label: "Tipo",     width: "100px" },
    { label: "Mesa",     width: "80px" },
    { label: "Mesero",   width: "150px" },
    { label: "Ítems",    width: "60px" },
    { label: "Total",    width: "100px" },
    { label: "Estado",   width: "120px" },
    { label: "Creado",   width: "150px" },
    { label: "Acciones", width: "120px" },
  ];

  const datos = ordenes.map((orden) => [
    `#${orden.id}`,
    orden.tipo_orden_display || orden.tipo_orden,
    orden.mesa_numero ? `Mesa ${orden.mesa_numero}` : "—",
    orden.usuario_nombre || orden.usuario,
    orden.detalles?.length || 0,
    `S/ ${parseFloat(orden.total).toFixed(2)}`,
    <StatusBadge key={`status-${orden.id}`} estado={orden.estado} />,
    new Date(orden.fecha_creacion).toLocaleString(),
    <button
      key={`comanda-${orden.id}`}
      onClick={() => window.open(`/comanda/${orden.id}`, "_blank")}
      disabled={orden.estado !== "abierta"}
      style={{
        padding: "4px 10px", borderRadius: "6px", border: "1px solid #2C5545",
        backgroundColor: "transparent", color: "#2C5545",
        fontFamily: "'Lato', sans-serif", fontSize: "12px", fontWeight: 600,
        cursor: orden.estado === "abierta" ? "pointer" : "not-allowed",
        opacity: orden.estado === "abierta" ? 1 : 0.4,
      }}
    >
      Comanda
    </button>,
  ]);

  return (
    <div>
      <PageHeader
        titulo="Órdenes"
        descripcion="Gestiona órdenes de mesas, para llevar y delivery"
        accion={
          <button
            onClick={() => setModalAbierto(true)}
            style={estilos.botonNuevo}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#1E4A37")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#2C5545")}
          >
            + Nueva Orden
          </button>
        }
      />

      {error && <div style={estilos.errorBanner}>⚠️ {error}</div>}

      {ordenes.length === 0 ? (
        <EmptyState titulo="Sin órdenes abiertas" subtitulo="Crea una nueva orden para comenzar" />
      ) : (
        <DataTable columnas={columnas} datos={datos} total={ordenes.length} />
      )}

      <FormModal
        abierto={modalAbierto}
        titulo="Crear Nueva Orden"
        onCerrar={() => setModalAbierto(false)}
        onGuardar={manejarGuardar}
        cargando={cargandoForm}
        maxWidth="600px"
        textoGuardar="Crear Orden"
      >
        <OrdenForm
          onSubmit={manejarCrearOrden}
          onSetSubmit={(fn) => { submitRef.current = fn; }}
          cargando={cargandoForm}
          mesas={mesas}
          productos={productos}
          promociones={promociones}
        />
      </FormModal>
    </div>
  );
}

const estilos = {
  botonNuevo: {
    padding: "10px 16px", borderRadius: "8px", border: "none",
    backgroundColor: "#2C5545", color: "white",
    fontFamily: "'Lato', sans-serif", fontSize: "13px", fontWeight: 600,
    cursor: "pointer", transition: "background-color 0.2s",
  },
  errorBanner: {
    padding: "12px 16px", marginBottom: "16px",
    backgroundColor: "#fdecea", border: "1px solid #f5bfb7",
    borderRadius: "8px", fontFamily: "'Lato', sans-serif",
    fontSize: "13px", color: "#c62828",
  },
};

import { useState, useEffect, useRef } from "react";
import PageHeader from "../../components/common/PageHeader";
import { FormModal } from "../../components/common/Modals";
import { LoadingSpinner, EmptyState } from "../../components/common/LoadingSpinner-EmptyState";
import DataTable from "../../components/common/DataTable";
import StatusBadge from "../../components/common/StatusBadge";
import OrdenForm from "./OrdenForm";
import ordenesService from "../../services/ordenesService";

export default function OrdenesPage() {
  const [ordenes, setOrdenes] = useState([]);
  const [mesas, setMesas] = useState([]);
  const [productos, setProductos] = useState([]);
  const [promociones, setPromociones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [cargandoFormulario, setCargandoFormulario] = useState(false);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [error, setError] = useState("");
  const submitFunctionRef = useRef(null);

  // Cargar órdenes, mesas, productos y promociones
  useEffect(() => {
    cargarDatos();
    // Refrescar cada 5 segundos para actualización en tiempo real
    const intervalo = setInterval(cargarDatos, 5000);
    return () => clearInterval(intervalo);
  }, []);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");

      // Obtener órdenes
      const respOrdenes = await ordenesService.getOrdenes();
      setOrdenes(respOrdenes.results || respOrdenes);

      // TODO: Cargar mesas, productos y promociones desde sus endpoints
      // Por ahora, usamos datos mock
      setMesas([
        { id: 1, numero: 1 },
        { id: 2, numero: 2 },
        { id: 3, numero: 3 },
        { id: 4, numero: 4 },
        { id: 5, numero: 5 },
      ]);

      setProductos([
        { id: 1, nombre: "Café Americano", precio: "2.50" },
        { id: 2, nombre: "Café Latte", precio: "3.50" },
        { id: 3, nombre: "Sándwich", precio: "4.00" },
        { id: 4, nombre: "Pastel", precio: "2.00" },
      ]);

      setPromociones([
        { id: 1, nombre: "Combo Café + Pastel", precio: "5.00" },
        { id: 2, nombre: "Combo Sándwich + Café", precio: "6.00" },
      ]);

      setCargando(false);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar datos");
      setCargando(false);
    }
  };

  const manejarGuardarOrden = async () => {
    if (submitFunctionRef.current) {
      setCargandoFormulario(true);
      try {
        await submitFunctionRef.current();
        setModalAbierto(false);
        setError("");
        // Recargar órdenes
        cargarDatos();
      } catch (err) {
        setError(err.response?.data?.detail || "Error al crear orden");
      } finally {
        setCargandoFormulario(false);
      }
    }
  };

  const manejarCrearOrden = async (datosOrden) => {
    const nuevaOrden = await ordenesService.crearOrden(
      datosOrden.tipoOrden,
      datosOrden.mesaId,
      datosOrden.detalles
    );
    setOrdenes([nuevaOrden, ...ordenes]);
  };

  if (cargando) return <LoadingSpinner />;

  const columnas = [
    { label: "ID", width: "60px" },
    { label: "Tipo", width: "100px" },
    { label: "Mesa", width: "80px" },
    { label: "Mesero", width: "150px" },
    { label: "Ítems", width: "60px" },
    { label: "Total", width: "100px" },
    { label: "Estado", width: "120px" },
    { label: "Creado", width: "150px" },
  ];

  const datos = ordenes.map((orden) => [
    `#${orden.id}`,
    orden.tipo_orden_display || orden.tipo_orden,
    orden.mesa_numero ? `Mesa ${orden.mesa_numero}` : "—",
    orden.usuario_nombre || orden.usuario,
    orden.detalles?.length || 0,
    `$${parseFloat(orden.total).toFixed(2)}`,
    <StatusBadge key={`status-${orden.id}`} estado={orden.estado} />,
    new Date(orden.fecha_creacion).toLocaleString(),
  ]);

  return (
    <div>
      <PageHeader
        titulo="Órdenes"
        descripcion="Gestiona órdenes de mesas y entregas para llevar"
        accion={
          <button
            onClick={() => setModalAbierto(true)}
            style={{
              padding: "10px 16px",
              borderRadius: "8px",
              border: "none",
              backgroundColor: "#2C5545",
              color: "white",
              fontFamily: "'Lato', sans-serif",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              transition: "background-color 0.2s",
            }}
            onMouseEnter={(e) => (e.target.style.backgroundColor = "#1E4A37")}
            onMouseLeave={(e) => (e.target.style.backgroundColor = "#2C5545")}
          >
            + Nueva Orden
          </button>
        }
      />

      {error && (
        <div
          style={{
            padding: "12px 16px",
            marginBottom: "16px",
            backgroundColor: "#fdecea",
            border: "1px solid #f5bfb7",
            borderRadius: "8px",
            fontFamily: "'Lato', sans-serif",
            fontSize: "13px",
            color: "#c62828",
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {ordenes.length === 0 ? (
        <EmptyState titulo="Sin órdenes abiertas" subtitulo="Crea una nueva orden para comenzar" />
      ) : (
        <DataTable columnas={columnas} datos={datos} total={ordenes.length} />
      )}

      <FormModal
        abierto={modalAbierto}
        titulo="Crear Nueva Orden"
        onCerrar={() => setModalAbierto(false)}
        onGuardar={manejarGuardarOrden}
        cargando={cargandoFormulario}
        maxWidth="600px"
        textoGuardar="Crear Orden"
      >
        <OrdenForm
          onSubmit={manejarCrearOrden}
          onSetSubmit={(fn) => {
            submitFunctionRef.current = fn;
          }}
          cargando={cargandoFormulario}
          mesas={mesas}
          productos={productos}
          promociones={promociones}
        />
      </FormModal>
    </div>
  );
}

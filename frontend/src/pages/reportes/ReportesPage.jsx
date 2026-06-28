import { useState } from "react";
import { FileDown, BarChart3, Package, Receipt } from "lucide-react";
import reporteService, { descargarBlob } from "../../services/reporteService";
import {
  PageHeader,
  DataTable,
  StatusBadge,
  SearchBar,
} from "../../components/common";

// ─── Fecha helpers ────────────────────────────────────────────────────────────
const hoy = () => new Date().toISOString().split("T")[0];
const hace30 = () => {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0];
};

// ─── Componente filtro de fechas ──────────────────────────────────────────────
function FiltroPeriodo({ fechaInicio, fechaFin, onChange, onBuscar, cargando }) {
  return (
    <div className="flex flex-wrap items-end gap-3 mb-4">
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <label style={{
          fontFamily: "'Lato', sans-serif", fontSize: 11,
          fontWeight: 700, color: "rgba(44,85,69,0.7)",
          letterSpacing: "0.07em", textTransform: "uppercase",
        }}>
          Desde
        </label>
        <input
          type="date"
          value={fechaInicio}
          onChange={(e) => onChange("fechaInicio", e.target.value)}
          style={{
            padding: "8px 12px", borderRadius: 8,
            border: "1px solid rgba(44,85,69,0.2)",
            fontFamily: "'Lato', sans-serif", fontSize: 13.5,
            color: "#333", outline: "none",
          }}
        />
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <label style={{
          fontFamily: "'Lato', sans-serif", fontSize: 11,
          fontWeight: 700, color: "rgba(44,85,69,0.7)",
          letterSpacing: "0.07em", textTransform: "uppercase",
        }}>
          Hasta
        </label>
        <input
          type="date"
          value={fechaFin}
          onChange={(e) => onChange("fechaFin", e.target.value)}
          style={{
            padding: "8px 12px", borderRadius: 8,
            border: "1px solid rgba(44,85,69,0.2)",
            fontFamily: "'Lato', sans-serif", fontSize: 13.5,
            color: "#333", outline: "none",
          }}
        />
      </div>
      <button
        onClick={onBuscar}
        disabled={cargando}
        style={{
          backgroundColor: "#2C5545", color: "white",
          border: "none", borderRadius: 8,
          padding: "9px 18px",
          fontFamily: "'Lato', sans-serif",
          fontSize: 13, fontWeight: 600,
          cursor: cargando ? "not-allowed" : "pointer",
          opacity: cargando ? 0.7 : 1,
        }}
      >
        {cargando ? "Consultando..." : "Consultar"}
      </button>
    </div>
  );
}

// ─── Botón exportar Excel ─────────────────────────────────────────────────────
function BtnExportar({ onClick, cargando }) {
  return (
    <button
      onClick={onClick}
      disabled={cargando}
      style={{
        display: "flex", alignItems: "center", gap: 6,
        backgroundColor: "white", color: "#2C5545",
        border: "1px solid rgba(44,85,69,0.3)",
        borderRadius: 8, padding: "8px 14px",
        fontFamily: "'Lato', sans-serif",
        fontSize: 12.5, fontWeight: 600,
        cursor: cargando ? "not-allowed" : "pointer",
        opacity: cargando ? 0.7 : 1,
      }}
    >
      <FileDown size={14} strokeWidth={2} />
      {cargando ? "Generando..." : "Exportar Excel"}
    </button>
  );
}

// ─── Tarjeta KPI ──────────────────────────────────────────────────────────────
function KpiCard({ label, valor, sub }) {
  return (
    <div style={{
      backgroundColor: "white", borderRadius: 12,
      padding: "18px 20px",
      border: "1px solid rgba(44,85,69,0.1)",
      boxShadow: "0 2px 8px rgba(44,85,69,0.06)",
      flex: 1, minWidth: 160,
    }}>
      <p style={{
        fontFamily: "'Lato', sans-serif", fontSize: 11,
        fontWeight: 700, color: "rgba(44,85,69,0.6)",
        letterSpacing: "0.08em", textTransform: "uppercase", margin: 0,
      }}>
        {label}
      </p>
      <p style={{
        fontFamily: "'Playfair Display', serif", fontSize: 26,
        fontWeight: 600, color: "#2C5545",
        margin: "6px 0 4px 0", lineHeight: 1,
      }}>
        {valor}
      </p>
      {sub && (
        <p style={{
          fontFamily: "'Lato', sans-serif", fontSize: 12,
          color: "rgba(44,85,69,0.55)", margin: 0,
        }}>
          {sub}
        </p>
      )}
    </div>
  );
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
const TABS = [
  { id: "ventas",    label: "Ventas",    icon: BarChart3 },
  { id: "productos", label: "Productos", icon: Package   },
  { id: "caja",      label: "Caja",      icon: Receipt   },
];

// ─── Página principal ─────────────────────────────────────────────────────────
export default function ReportesPage() {
  const [tab, setTab]                   = useState("ventas");
  const [fechaInicio, setFechaInicio]   = useState(hace30());
  const [fechaFin, setFechaFin]         = useState(hoy());
  const [cargando, setCargando]         = useState(false);
  const [exportando, setExportando]     = useState(false);
  const [error, setError]               = useState(null);
  const [dataVentas, setDataVentas]     = useState(null);
  const [dataProductos, setDataProductos] = useState(null);
  const [dataCaja, setDataCaja]         = useState(null);

  const handleChange = (campo, valor) => {
    if (campo === "fechaInicio") setFechaInicio(valor);
    else setFechaFin(valor);
  };

  const handleConsultar = async () => {
    if (!fechaInicio || !fechaFin) return;
    try {
      setCargando(true);
      setError(null);
      const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin };

      if (tab === "ventas") {
        const { data } = await reporteService.getVentas(params);
        setDataVentas(data);
      } else if (tab === "productos") {
        const { data } = await reporteService.getProductos(params);
        setDataProductos(data);
      } else {
        const { data } = await reporteService.getCaja(params);
        setDataCaja(data);
      }
    } catch {
      setError("Error al consultar el reporte. Verifica el rango de fechas.");
    } finally {
      setCargando(false);
    }
  };

  const handleExportar = async () => {
    try {
      setExportando(true);
      const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin };
      let res, nombre;

      if (tab === "ventas") {
        res = await reporteService.exportarVentas(params);
        nombre = `reporte_ventas_${fechaInicio}_${fechaFin}.xlsx`;
      } else if (tab === "productos") {
        res = await reporteService.exportarProductos(params);
        nombre = `reporte_productos_${fechaInicio}_${fechaFin}.xlsx`;
      } else {
        res = await reporteService.exportarCaja(params);
        nombre = `reporte_caja_${fechaInicio}_${fechaFin}.xlsx`;
      }
      descargarBlob(res.data, nombre);
    } catch {
      setError("Error al exportar. Intenta nuevamente.");
    } finally {
      setExportando(false);
    }
  };

  // ── Columnas por tab ────────────────────────────────────────────────────────
  const columnasVentasDia = [
    { label: "Fecha", key: "dia" },
    {
      label: "Total (S/)", key: "total",
      render: (r) => `S/ ${Number(r.total).toFixed(2)}`,
    },
    { label: "Órdenes", key: "ordenes" },
  ];

  const columnasMetodo = [
    { label: "Método de pago", key: "metodo_pago" },
    {
      label: "Total (S/)", key: "total",
      render: (r) => `S/ ${Number(r.total).toFixed(2)}`,
    },
    { label: "Cantidad", key: "cantidad" },
  ];

  const columnasProductos = [
    { label: "Producto", key: "nombre" },
    { label: "Categoría", key: "categoria" },
    { label: "Cantidad vendida", key: "cantidad" },
    {
      label: "Total (S/)", key: "total",
      render: (r) => `S/ ${Number(r.total).toFixed(2)}`,
    },
  ];

  const columnasTurnos = [
    { label: "Caja #", key: "caja_id" },
    { label: "Cajero", key: "cajero" },
    {
      label: "Estado", key: "estado",
      render: (r) => <StatusBadge estado={r.estado} />,
    },
    {
      label: "Apertura", key: "fecha_apertura",
      render: (r) => r.fecha_apertura
        ? new Date(r.fecha_apertura).toLocaleString("es-PE")
        : "—",
    },
    {
      label: "Total ventas", key: "total_ventas",
      render: (r) => `S/ ${Number(r.total_ventas).toFixed(2)}`,
    },
    {
      label: "Diferencia", key: "diferencia",
      render: (r) => r.diferencia !== null
        ? <span style={{ color: r.diferencia >= 0 ? "#2e7d32" : "#c62828", fontWeight: 600 }}>
            {r.diferencia >= 0 ? "+" : ""}S/ {Number(r.diferencia).toFixed(2)}
          </span>
        : "—",
    },
  ];

  return (
    <>
      <PageHeader
        titulo="Reportes"
        descripcion="Consulta y exporta reportes de ventas, productos y caja"
        accion={<BtnExportar onClick={handleExportar} cargando={exportando} />}
      />

      {/* Tabs */}
      <div className="flex gap-2 mb-5">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setTab(id); setError(null); }}
            style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "8px 16px", borderRadius: 8,
              border: "1px solid",
              borderColor: tab === id ? "#2C5545" : "rgba(44,85,69,0.2)",
              backgroundColor: tab === id ? "#2C5545" : "white",
              color: tab === id ? "white" : "#2C5545",
              fontFamily: "'Lato', sans-serif",
              fontSize: 13, fontWeight: 600,
              cursor: "pointer",
            }}
          >
            <Icon size={14} strokeWidth={2} />
            {label}
          </button>
        ))}
      </div>

      {/* Filtro de período */}
      <FiltroPeriodo
        fechaInicio={fechaInicio}
        fechaFin={fechaFin}
        onChange={handleChange}
        onBuscar={handleConsultar}
        cargando={cargando}
      />

      {error && (
        <div style={{
          marginBottom: 16, padding: "10px 14px",
          backgroundColor: "#fdecea", color: "#c62828",
          borderRadius: 8, fontFamily: "'Lato', sans-serif", fontSize: 13,
        }}>
          {error}
        </div>
      )}

      {/* ── Tab Ventas ─────────────────────────────────────────────────────── */}
      {tab === "ventas" && dataVentas && (
        <div className="flex flex-col gap-5">
          {/* KPIs */}
          <div className="flex flex-wrap gap-3">
            <KpiCard
              label="Total ventas"
              valor={`S/ ${Number(dataVentas.total_ventas).toFixed(2)}`}
              sub={`${dataVentas.total_ordenes} órdenes`}
            />
            <KpiCard
              label="Ticket promedio"
              valor={`S/ ${Number(dataVentas.ticket_promedio).toFixed(2)}`}
            />
          </div>
          {/* Ventas por día */}
          <div>
            <p style={{
              fontFamily: "'Lato', sans-serif", fontSize: 11,
              fontWeight: 700, color: "rgba(44,85,69,0.7)",
              letterSpacing: "0.08em", textTransform: "uppercase",
              marginBottom: 8,
            }}>
              Ventas por día
            </p>
            <DataTable
              columnas={columnasVentasDia}
              datos={dataVentas.ventas_por_dia ?? []}
              total={dataVentas.ventas_por_dia?.length ?? 0}
              textoVacio="Sin datos en este período"
            />
          </div>
          {/* Por método de pago */}
          <div>
            <p style={{
              fontFamily: "'Lato', sans-serif", fontSize: 11,
              fontWeight: 700, color: "rgba(44,85,69,0.7)",
              letterSpacing: "0.08em", textTransform: "uppercase",
              marginBottom: 8,
            }}>
              Por método de pago
            </p>
            <DataTable
              columnas={columnasMetodo}
              datos={dataVentas.ventas_por_metodo_pago ?? []}
              total={dataVentas.ventas_por_metodo_pago?.length ?? 0}
              textoVacio="Sin datos"
            />
          </div>
        </div>
      )}

      {/* ── Tab Productos ──────────────────────────────────────────────────── */}
      {tab === "productos" && dataProductos && (
        <div className="flex flex-col gap-5">
          <div>
            <p style={{
              fontFamily: "'Lato', sans-serif", fontSize: 11,
              fontWeight: 700, color: "rgba(44,85,69,0.7)",
              letterSpacing: "0.08em", textTransform: "uppercase",
              marginBottom: 8,
            }}>
              Productos más vendidos
            </p>
            <DataTable
              columnas={columnasProductos}
              datos={dataProductos.productos ?? []}
              total={dataProductos.productos?.length ?? 0}
              textoVacio="Sin productos vendidos en este período"
            />
          </div>
          {dataProductos.promociones?.length > 0 && (
            <div>
              <p style={{
                fontFamily: "'Lato', sans-serif", fontSize: 11,
                fontWeight: 700, color: "rgba(44,85,69,0.7)",
                letterSpacing: "0.08em", textTransform: "uppercase",
                marginBottom: 8,
              }}>
                Promociones más vendidas
              </p>
              <DataTable
                columnas={[
                  { label: "Promoción", key: "nombre" },
                  { label: "Cantidad", key: "cantidad" },
                  {
                    label: "Total (S/)", key: "total",
                    render: (r) => `S/ ${Number(r.total).toFixed(2)}`,
                  },
                ]}
                datos={dataProductos.promociones}
                total={dataProductos.promociones.length}
                textoVacio="Sin promociones vendidas"
              />
            </div>
          )}
        </div>
      )}

      {/* ── Tab Caja ───────────────────────────────────────────────────────── */}
      {tab === "caja" && dataCaja && (
        <div>
          <p style={{
            fontFamily: "'Lato', sans-serif", fontSize: 11,
            fontWeight: 700, color: "rgba(44,85,69,0.7)",
            letterSpacing: "0.08em", textTransform: "uppercase",
            marginBottom: 8,
          }}>
            Turnos de caja
          </p>
          <DataTable
            columnas={columnasTurnos}
            datos={dataCaja.turnos ?? []}
            total={dataCaja.turnos?.length ?? 0}
            textoVacio="Sin turnos en este período"
          />
        </div>
      )}

      {/* Estado vacío inicial */}
      {!cargando && !dataVentas && !dataProductos && !dataCaja && !error && (
        <div style={{
          textAlign: "center", padding: "60px 0",
          color: "rgba(44,85,69,0.45)",
          fontFamily: "'Lato', sans-serif", fontSize: 14,
        }}>
          Selecciona un período y presiona <strong>Consultar</strong> para ver el reporte.
        </div>
      )}
    </>
  );
}
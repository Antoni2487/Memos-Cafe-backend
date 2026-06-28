import { useState } from "react";
import { Download, FileSpreadsheet, TrendingUp, ShoppingBag } from "lucide-react";
import api from "../../services/api";

const COLOR = {
  verde:    "#2C5545",
  verdeOsc: "#1E4A37",
  verdePal: "rgba(44,85,69,0.08)",
  borde:    "rgba(44,85,69,0.12)",
  dorado:   "#C9A84C",
};

function StatCard({ label, value }) {
  return (
    <div style={{ background: "white", border: `1.5px solid ${COLOR.borde}`,
      borderRadius: 12, padding: "16px 20px" }}>
      <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
        color: "rgba(44,85,69,0.6)", textTransform: "uppercase",
        letterSpacing: "0.07em", margin: "0 0 6px 0" }}>{label}</p>
      <p style={{ fontFamily: "'Playfair Display',Georgia,serif",
        fontSize: 24, fontWeight: 700, color: COLOR.verde, margin: 0 }}>{value}</p>
    </div>
  );
}

export default function ReportesPage() {
  const hoy = new Date().toISOString().split("T")[0];
  const [fechaInicio, setFechaInicio] = useState(hoy);
  const [fechaFin, setFechaFin]       = useState(hoy);
  const [datos, setDatos]             = useState(null);
  const [cargando, setCargando]       = useState(false);
  const [exportando, setExportando]   = useState(false);
  const [error, setError]             = useState("");

  const consultarReporte = async () => {
    setCargando(true);
    setError("");
    setDatos(null);
    try {
      const { data } = await api.get("/reportes/ventas/", {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
      });
      setDatos(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Error al consultar reporte");
    } finally {
      setCargando(false);
    }
  };

  const exportarExcel = async () => {
    setExportando(true);
    setError("");
    try {
      const response = await api.get("/reportes/ventas/export/", {
        params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a   = document.createElement("a");
      a.href    = url;
      a.download = `reporte_ventas_${fechaInicio}_${fechaFin}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError("Error al exportar Excel");
    } finally {
      setExportando(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

      {/* Encabezado */}
      <div style={{ borderBottom: `1px solid ${COLOR.borde}`, paddingBottom: 16 }}>
        <h2 style={{ fontFamily: "'Playfair Display',Georgia,serif", fontSize: "1.5rem",
          fontWeight: 600, color: COLOR.verde, margin: 0 }}>Reportes</h2>
        <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
          color: "rgba(44,85,69,0.6)", margin: "4px 0 0 0" }}>
          Generá y exportá reportes de ventas
        </p>
      </div>

      {/* Filtros */}
      <div style={{ background: "white", border: `1.5px solid ${COLOR.borde}`,
        borderRadius: 12, padding: "18px 20px" }}>
        <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
          color: "rgba(44,85,69,0.6)", textTransform: "uppercase",
          letterSpacing: "0.07em", margin: "0 0 14px 0" }}>Período</p>

        <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
          <div>
            <label style={estilos.inputLabel}>Desde</label>
            <input type="date" value={fechaInicio}
              onChange={e => setFechaInicio(e.target.value)}
              style={estilos.input} />
          </div>
          <div>
            <label style={estilos.inputLabel}>Hasta</label>
            <input type="date" value={fechaFin}
              onChange={e => setFechaFin(e.target.value)}
              style={estilos.input} />
          </div>
          <button onClick={consultarReporte} disabled={cargando}
            style={{ ...estilos.btn, background: cargando ? "#aaa" : COLOR.verde }}>
            <TrendingUp size={14} />
            {cargando ? "Consultando..." : "Consultar"}
          </button>
          <button onClick={exportarExcel} disabled={exportando}
            style={{ ...estilos.btn, background: exportando ? "#aaa" : COLOR.dorado }}>
            <Download size={14} />
            {exportando ? "Exportando..." : "Exportar Excel"}
          </button>
        </div>

        {error && (
          <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
            color: "#c62828", margin: "12px 0 0 0" }}>⚠️ {error}</p>
        )}
      </div>

      {/* Resultados */}
      {datos && (
        <>
          {/* KPIs */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
            <StatCard label="Total ventas"
              value={`S/ ${parseFloat(datos.total_ventas).toFixed(2)}`} />
            <StatCard label="Total órdenes" value={datos.total_ordenes} />
            <StatCard label="Ticket promedio"
              value={`S/ ${parseFloat(datos.ticket_promedio).toFixed(2)}`} />
          </div>

          {/* Ventas por día */}
          {datos.ventas_por_dia?.length > 0 && (
            <div style={{ background: "white", border: `1.5px solid ${COLOR.borde}`,
              borderRadius: 12, overflow: "hidden" }}>
              <div style={{ padding: "14px 20px", borderBottom: `1px solid ${COLOR.borde}`,
                display: "flex", alignItems: "center", gap: 8 }}>
                <TrendingUp size={16} color={COLOR.verde} />
                <span style={{ fontFamily: "'Playfair Display',Georgia,serif",
                  fontSize: 15, fontWeight: 600, color: COLOR.verde }}>
                  Ventas por día
                </span>
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: COLOR.verdePal }}>
                    {["Fecha", "Total (S/)", "Órdenes"].map(h => (
                      <th key={h} style={estilos.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {datos.ventas_por_dia.map((row, i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${COLOR.borde}` }}>
                      <td style={estilos.td}>{row.fecha}</td>
                      <td style={estilos.td}>S/ {parseFloat(row.total).toFixed(2)}</td>
                      <td style={estilos.td}>{row.ordenes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Por método de pago */}
          {datos.ventas_por_metodo_pago?.length > 0 && (
            <div style={{ background: "white", border: `1.5px solid ${COLOR.borde}`,
              borderRadius: 12, overflow: "hidden" }}>
              <div style={{ padding: "14px 20px", borderBottom: `1px solid ${COLOR.borde}`,
                display: "flex", alignItems: "center", gap: 8 }}>
                <ShoppingBag size={16} color={COLOR.verde} />
                <span style={{ fontFamily: "'Playfair Display',Georgia,serif",
                  fontSize: 15, fontWeight: 600, color: COLOR.verde }}>
                  Por método de pago
                </span>
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: COLOR.verdePal }}>
                    {["Método", "Total (S/)", "Cantidad"].map(h => (
                      <th key={h} style={estilos.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {datos.ventas_por_metodo_pago.map((row, i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${COLOR.borde}` }}>
                      <td style={estilos.td}>{row.metodo_pago}</td>
                      <td style={estilos.td}>S/ {parseFloat(row.total).toFixed(2)}</td>
                      <td style={estilos.td}>{row.cantidad}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {datos.total_ordenes === 0 && (
            <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
              color: "#999", textAlign: "center", padding: 20 }}>
              Sin ventas en el período seleccionado
            </p>
          )}
        </>
      )}
    </div>
  );
}

const estilos = {
  inputLabel: { fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
    color: "rgba(44,85,69,0.75)", textTransform: "uppercase", letterSpacing: "0.07em",
    display: "block", marginBottom: 5 },
  input: { padding: "9px 12px", borderRadius: 8, border: "1px solid rgba(44,85,69,0.2)",
    fontFamily: "'Lato',sans-serif", fontSize: 13, color: "#333", outline: "none" },
  btn: { display: "flex", alignItems: "center", gap: 6, padding: "10px 16px",
    borderRadius: 8, border: "none", color: "white", fontFamily: "'Lato',sans-serif",
    fontSize: 13, fontWeight: 600, cursor: "pointer" },
  th: { padding: "10px 16px", textAlign: "left", fontFamily: "'Lato',sans-serif",
    fontSize: 11, fontWeight: 700, color: "rgba(44,85,69,0.6)",
    textTransform: "uppercase", letterSpacing: "0.07em" },
  td: { padding: "10px 16px", fontFamily: "'Lato',sans-serif", fontSize: 13, color: "#444" },
};

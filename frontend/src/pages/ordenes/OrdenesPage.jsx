import { useState, useEffect } from "react";
import { ClipboardList, UtensilsCrossed, Bike, ShoppingBag, Plus, Minus, Trash2, Printer, Ban, PenLine, X, Eye } from "lucide-react";
import ordenesService from "../../services/ordenesService";
import mesasService from "../../services/mesasService";
import productoService from "../../services/productoService";
import { TIPO_ORDEN, PLATAFORMA_DELIVERY } from "../../utils/constants";
import { formatDateTime } from "../../utils/formatters";
import StatusBadge from "../../components/common/StatusBadge";
import { ConfirmDialog } from "../../components/common/Modals";
import { useIsMobile } from "../../hooks/useMediaQuery";

const PLATAFORMA_OPCIONES = [
  { value: PLATAFORMA_DELIVERY.RAPPI,      label: "Rappi" },
  { value: PLATAFORMA_DELIVERY.PEDIDOS_YA, label: "PedidosYa" },
  { value: PLATAFORMA_DELIVERY.DIDI,       label: "DiDi Food" },
  { value: PLATAFORMA_DELIVERY.OTRO,       label: "Otro" },
];

const TIPO_TABS = [
  { value: TIPO_ORDEN.MESA,     label: "Mesa",      Icon: UtensilsCrossed },
  { value: TIPO_ORDEN.LLEVAR,   label: "Para llevar", Icon: ShoppingBag },
  { value: TIPO_ORDEN.DELIVERY, label: "Delivery",  Icon: Bike },
];

const COLOR = {
  verde:    "#2C5545",
  verdeOsc: "#1E4A37",
  verdePal: "rgba(44,85,69,0.08)",
  rojo:     "#d4183d",
  rojoPal:  "rgba(212,24,61,0.08)",
  dorado:   "#C9A84C",
  gris:     "#f5f5f5",
  borde:    "rgba(44,85,69,0.12)",
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function estadoMesaColor(estado) {
  if (estado === "libre")    return { bg: "#e8f5e9", color: "#2e7d32", borde: "#a5d6a7" };
  if (estado === "ocupada")  return { bg: "#fdecea", color: "#c62828", borde: "#f5bfb7" };
  return { bg: "#fff8e1", color: "#f57f17", borde: "#ffe082" };
}

// ─── Card de mesa ─────────────────────────────────────────────────────────────
function MesaCard({ mesa, seleccionada, onClick }) {
  const { bg, color, borde } = estadoMesaColor(mesa.estado);
  const ocupada = mesa.estado === "ocupada";
  return (
    <button
      onClick={() => !ocupada && onClick(mesa)}
      disabled={ocupada}
      style={{
        background: seleccionada ? COLOR.verde : bg,
        border: `2px solid ${seleccionada ? COLOR.verde : borde}`,
        borderRadius: 12, padding: "14px 10px",
        cursor: ocupada ? "not-allowed" : "pointer",
        display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
        transition: "all 0.15s", opacity: ocupada ? 0.6 : 1,
        minWidth: 90,
      }}
    >
      <UtensilsCrossed size={20} color={seleccionada ? "white" : color} />
      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 13, fontWeight: 700,
        color: seleccionada ? "white" : color }}>
        Mesa {mesa.numero}
      </span>
      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 10, fontWeight: 600,
        color: seleccionada ? "rgba(255,255,255,0.8)" : color,
        textTransform: "uppercase", letterSpacing: "0.06em" }}>
        {mesa.estado}
      </span>
      {mesa.capacidad && (
        <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 10,
          color: seleccionada ? "rgba(255,255,255,0.65)" : "rgba(0,0,0,0.4)" }}>
          {mesa.capacidad} personas
        </span>
      )}
    </button>
  );
}

// ─── Card de producto ─────────────────────────────────────────────────────────
function ProductoCard({ item, esPromo = false, onClick }) {
  const precio = parseFloat(item.precio ?? 0);
  return (
    <button
      onClick={() => onClick(item, esPromo)}
      style={{
        background: "white", border: `1.5px solid ${COLOR.borde}`,
        borderRadius: 10, padding: "12px 10px", cursor: "pointer",
        display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 4,
        textAlign: "left", transition: "all 0.15s", width: "100%",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = COLOR.verde;
        e.currentTarget.style.boxShadow = `0 2px 12px ${COLOR.verdePal}`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = COLOR.borde;
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {esPromo && (
        <span style={{ fontSize: 10, fontWeight: 700, color: COLOR.dorado,
          textTransform: "uppercase", letterSpacing: "0.06em" }}>
          Promo
        </span>
      )}
      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 13, fontWeight: 600,
        color: COLOR.verde, lineHeight: 1.3 }}>
        {item.nombre}
      </span>
      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 14, fontWeight: 700,
        color: COLOR.verde }}>
        S/ {precio.toFixed(2)}
      </span>
    </button>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────
export default function OrdenesPage() {
  const isMobile = useIsMobile();

  // Datos
  const [ordenes, setOrdenes]         = useState([]);
  const [mesas, setMesas]             = useState([]);
  const [productos, setProductos]     = useState([]);
  const [promociones, setPromociones] = useState([]);
  const [cargando, setCargando]       = useState(true);
  const [error, setError]             = useState("");

  // Orden en construcción
  const [tipoOrden, setTipoOrden]     = useState(TIPO_ORDEN.MESA);
  const [mesaId, setMesaId]           = useState(null);
  const [items, setItems]             = useState([]);
  const [clienteNombre, setClienteNombre]       = useState("");
  const [clienteTelefono, setClienteTelefono]   = useState("");
  const [direccionEntrega, setDireccionEntrega] = useState("");
  const [plataforma, setPlataforma]             = useState("");
  const [plataformaOtra, setPlataformaOtra]     = useState("");
  const [errForm, setErrForm]         = useState({});
  const [creando, setCreando]         = useState(false);
  const [exitoMsg, setExitoMsg]       = useState("");

  // Filtro catálogo
  const [categFiltro, setCategFiltro] = useState("todos");

  // Anular
  const [anularTarget, setAnularTarget] = useState(null);
  const [anulando, setAnulando]         = useState(false);

  // Drawer editar/ver orden
  const [ordenEditar, setOrdenEditar]   = useState(null);
  const [drawerModo, setDrawerModo]     = useState("editar"); // "editar" | "ver"
  const [itemsEditar, setItemsEditar]   = useState([]);
  const [agregando, setAgregando]       = useState(false);
  const [editExito, setEditExito]       = useState("");

  // ── Carga inicial ────────────────────────────────────────────────────────────
  const cargarOrdenes = async () => {
    try {
      const { data } = await ordenesService.listar();
      setOrdenes(data.results ?? data);
    } catch { /* silencioso */ }
  };

  useEffect(() => {
    const init = async () => {
      setCargando(true);
      try {
        const [resO, resM, resP, resPr] = await Promise.all([
          ordenesService.listar(),
          mesasService.listar(),
          productoService.listar(),
          productoService.listarPromociones(),
        ]);
        setOrdenes(resO.data.results   ?? resO.data);
        setMesas(resM.data.results     ?? resM.data);
        setProductos(resP.data.results ?? resP.data);
        setPromociones(resPr.data.results ?? resPr.data);
      } catch (e) {
        setError("Error al cargar datos");
      } finally {
        setCargando(false);
      }
    };
    init();
    const iv = setInterval(cargarOrdenes, 5000);
    return () => clearInterval(iv);
  }, []);

  // ── Catálogo ─────────────────────────────────────────────────────────────────
  const CATEG_PROMOS = "__promociones__";
  const categorias = [
    "todos",
    ...new Set(productos.map((p) => p.categoria_nombre).filter(Boolean)),
    ...(promociones.length > 0 ? [CATEG_PROMOS] : []),
  ];

  const productosFiltrados = categFiltro === "todos"
    ? productos
    : categFiltro === CATEG_PROMOS
      ? []
      : productos.filter((p) => p.categoria_nombre === categFiltro);

  const promocionesFiltradas = (categFiltro === "todos" || categFiltro === CATEG_PROMOS)
    ? promociones
    : [];

  // ── Manejo de items ───────────────────────────────────────────────────────────
  const agregarItem = (item, esPromo) => {
    setItems((prev) => {
      const key = esPromo ? `promo-${item.id}` : `prod-${item.id}`;
      const existe = prev.find((i) => i.key === key);
      if (existe) return prev.map((i) => i.key === key ? { ...i, cantidad: i.cantidad + 1 } : i);
      return [...prev, {
        key, id: item.id, nombre: item.nombre,
        precio: parseFloat(item.precio ?? 0),
        esPromo, cantidad: 1, nota: "",
      }];
    });
  };

  const cambiarCantidad = (key, delta) => {
    setItems((prev) => prev
      .map((i) => i.key === key ? { ...i, cantidad: i.cantidad + delta } : i)
      .filter((i) => i.cantidad > 0)
    );
  };

  const quitarItem = (key) => setItems((prev) => prev.filter((i) => i.key !== key));

  const total = items.reduce((s, i) => s + i.precio * i.cantidad, 0);

  // ── Crear orden ───────────────────────────────────────────────────────────────
  const resetForm = () => {
    setItems([]); setMesaId(null); setErrForm({});
    setClienteNombre(""); setClienteTelefono("");
    setDireccionEntrega(""); setPlataforma(""); setPlataformaOtra("");
  };

  const handleCrear = async () => {
    const err = {};
    if (tipoOrden === TIPO_ORDEN.MESA && !mesaId) err.mesa = "Seleccioná una mesa";
    if (tipoOrden === TIPO_ORDEN.DELIVERY && !plataforma) err.plataforma = "Seleccioná la plataforma";
    if (tipoOrden === TIPO_ORDEN.DELIVERY && plataforma === PLATAFORMA_DELIVERY.OTRO && !plataformaOtra.trim())
      err.plataformaOtra = "Escribí el nombre";
    if (items.length === 0) err.items = "Agregá al menos un ítem";
    if (Object.keys(err).length) { setErrForm(err); return; }

    setCreando(true); setErrForm({});
    try {
      const payload = {
        tipo_orden: tipoOrden,
        mesa: tipoOrden === TIPO_ORDEN.MESA ? mesaId : null,
        detalles: items.map((i) => ({
          producto:  !i.esPromo ? i.id : null,
          promocion: i.esPromo  ? i.id : null,
          cantidad: i.cantidad,
          nota: i.nota || "",
        })),
      };
      if (tipoOrden === TIPO_ORDEN.DELIVERY) {
        payload.cliente_nombre    = clienteNombre;
        payload.cliente_telefono  = clienteTelefono;
        payload.direccion_entrega = direccionEntrega;
        payload.plataforma_delivery = plataforma;
        if (plataforma === PLATAFORMA_DELIVERY.OTRO) payload.plataforma_otra = plataformaOtra;
      }
      const { data } = await ordenesService.crear(payload);
      setOrdenes((prev) => [data, ...prev]);
      // Actualización optimista: la mesa ya está ocupada en la BD,
      // reflejarlo inmediatamente en el estado local sin esperar el polling.
      if (tipoOrden === TIPO_ORDEN.MESA && mesaId) {
        setMesas((prev) => prev.map((m) => m.id === mesaId ? { ...m, estado: "ocupada" } : m));
      }
      resetForm();
      setExitoMsg(`Orden #${data.id} creada`);
      setTimeout(() => setExitoMsg(""), 3000);
    } catch (e) {
      setErrForm({ api: e.response?.data?.detail || "Error al crear la orden" });
    } finally {
      setCreando(false);
    }
  };

  // ── Anular ────────────────────────────────────────────────────────────────────
  const handleAnular = async () => {
    if (!anularTarget) return;
    setAnulando(true);
    try {
      const { data } = await ordenesService.anular(anularTarget.id);
      setOrdenes((prev) => prev.map((o) => o.id === data.id ? data : o));
      setAnularTarget(null);
      // refrescar mesas para reflejar la liberación
      const resMesas = await mesasService.listar();
      setMesas(resMesas.data.results ?? resMesas.data);
    } catch (e) {
      alert(e.response?.data?.detail || "Error al anular");
    } finally {
      setAnulando(false);
    }
  };

  // ── Drawer editar ───────────────────────────────────────────────────────────────
  const abrirEditar = (orden) => {
    setOrdenEditar(orden);
    setDrawerModo("editar");
    setItemsEditar([]);
    setEditExito("");
  };

  const abrirVer = (orden) => {
    setOrdenEditar(orden);
    setDrawerModo("ver");
    setItemsEditar([]);
    setEditExito("");
  };

  const agregarItemEditar = (item, esPromo) => {
    setItemsEditar((prev) => {
      const key = esPromo ? `promo-${item.id}` : `prod-${item.id}`;
      const existe = prev.find((i) => i.key === key);
      if (existe) return prev.map((i) => i.key === key ? { ...i, cantidad: i.cantidad + 1 } : i);
      return [...prev, { key, id: item.id, nombre: item.nombre,
        precio: parseFloat(item.precio ?? 0), esPromo, cantidad: 1 }];
    });
  };

  const cambiarCantidadEditar = (key, delta) => {
    setItemsEditar((prev) => prev
      .map((i) => i.key === key ? { ...i, cantidad: i.cantidad + delta } : i)
      .filter((i) => i.cantidad > 0)
    );
  };

  const handleEliminarDetalle = async (detalleId, impreso) => {
    if (!ordenEditar) return;
    if (impreso) {
      const ok = window.confirm("Este ítem ya fue enviado a cocina. ¿Querés eliminarlo igual?");
      if (!ok) return;
    }
    try {
      const { data } = await ordenesService.eliminarDetalle(ordenEditar.id, detalleId);
      setOrdenes((prev) => prev.map((o) => o.id === data.id ? data : o));
      setOrdenEditar(data);
    } catch (e) {
      alert(e.response?.data?.detail || "Error al eliminar ítem");
    }
  };

  const handleConfirmarEditar = async () => {
    if (!ordenEditar || itemsEditar.length === 0) return;
    setAgregando(true);
    try {
      let ordenActual = ordenEditar;
      for (const item of itemsEditar) {
        const payload = {
          producto:  !item.esPromo ? item.id : null,
          promocion: item.esPromo  ? item.id : null,
          cantidad: item.cantidad,
          nota: "",
        };
        const { data } = await ordenesService.agregarDetalle(ordenActual.id, payload);
        ordenActual = data;
      }
      setOrdenes((prev) => prev.map((o) => o.id === ordenActual.id ? ordenActual : o));
      setOrdenEditar(ordenActual);
      setItemsEditar([]);
      setEditExito(`${itemsEditar.length} ítem(s) agregado(s)`);
      setTimeout(() => setEditExito(""), 3000);
    } catch (e) {
      alert(e.response?.data?.detail || "Error al agregar ítems");
    } finally {
      setAgregando(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────────
  if (cargando) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
      <p style={{ fontFamily: "'Lato',sans-serif", color: COLOR.verde, fontSize: 14 }}>Cargando...</p>
    </div>
  );

  const mesaSeleccionada = mesas.find((m) => m.id === mesaId);
  const drawerAncho = isMobile ? "100%" : 420;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

      {/* ── Encabezado ── */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", justifyContent: "space-between",
        borderBottom: `1px solid ${COLOR.borde}`, paddingBottom: 16 }}>
        <div>
          <h2 style={{ fontFamily: "'Playfair Display',Georgia,serif", fontSize: "1.5rem",
            fontWeight: 600, color: COLOR.verde, margin: 0 }}>Órdenes</h2>
          <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
            color: "rgba(44,85,69,0.6)", margin: "4px 0 0 0" }}>
            Creá y gestioná las órdenes del local
          </p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <div style={estilos.statPill}>
            <ClipboardList size={14} color={COLOR.verde} />
            <span>{ordenes.filter(o => o.estado === "abierta").length} abiertas</span>
          </div>
        </div>
      </div>

      {/* ── Panel principal: catálogo + orden ── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: isMobile ? "1fr" : "1fr 380px",
        gap: 20, alignItems: "start"
      }}>

        {/* ── Panel izquierdo: catálogo ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          {/* Tabs tipo orden */}
          <div style={{ display: "flex", gap: 8, background: COLOR.gris,
            borderRadius: 10, padding: 4, width: "fit-content" }}>
            {TIPO_TABS.map(({ value, label, Icon }) => (
              <button key={value} onClick={() => { setTipoOrden(value); setMesaId(null); setErrForm({}); }}
                style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "8px 16px", borderRadius: 8, border: "none", cursor: "pointer",
                  fontFamily: "'Lato',sans-serif", fontSize: 13, fontWeight: 600,
                  background: tipoOrden === value ? COLOR.verde : "transparent",
                  color: tipoOrden === value ? "white" : "rgba(44,85,69,0.6)",
                  transition: "all 0.15s",
                }}>
                <Icon size={14} />
                {label}
              </button>
            ))}
          </div>

          {/* Mesas (solo si tipo mesa) */}
          {tipoOrden === TIPO_ORDEN.MESA && (
            <div style={estilos.seccion}>
              <p style={estilos.seccionLabel}>Seleccioná una mesa</p>
              {errForm.mesa && <p style={estilos.errorTxt}>{errForm.mesa}</p>}
              {mesas.length === 0 ? (
                <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13, color: "#999" }}>
                  Sin mesas disponibles
                </p>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                  {mesas.filter(m => m.activo !== false).map((m) => (
                    <MesaCard key={m.id} mesa={m}
                      seleccionada={mesaId === m.id}
                      onClick={(m) => setMesaId(m.id)} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Campos delivery */}
          {tipoOrden === TIPO_ORDEN.DELIVERY && (
            <div style={estilos.seccion}>
              <p style={estilos.seccionLabel}>Datos del delivery</p>
              <div style={{ display: "grid", gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr", gap: 12 }}>
                <div style={{ gridColumn: isMobile ? "auto" : "1 / -1" }}>
                  <label style={estilos.inputLabel}>Plataforma *</label>
                  <select value={plataforma} onChange={e => setPlataforma(e.target.value)} style={estilos.select}>
                    <option value="">— Seleccioná —</option>
                    {PLATAFORMA_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                  {errForm.plataforma && <p style={estilos.errorTxt}>{errForm.plataforma}</p>}
                </div>
                {plataforma === PLATAFORMA_DELIVERY.OTRO && (
                  <div style={{ gridColumn: isMobile ? "auto" : "1 / -1" }}>
                    <label style={estilos.inputLabel}>Nombre de plataforma *</label>
                    <input value={plataformaOtra} onChange={e => setPlataformaOtra(e.target.value)} style={estilos.input} />
                    {errForm.plataformaOtra && <p style={estilos.errorTxt}>{errForm.plataformaOtra}</p>}
                  </div>
                )}
                <div>
                  <label style={estilos.inputLabel}>Cliente</label>
                  <input value={clienteNombre} onChange={e => setClienteNombre(e.target.value)} style={estilos.input} placeholder="Nombre" />
                </div>
                <div>
                  <label style={estilos.inputLabel}>Teléfono</label>
                  <input value={clienteTelefono} onChange={e => setClienteTelefono(e.target.value)} style={estilos.input} placeholder="999 999 999" />
                </div>
                <div style={{ gridColumn: isMobile ? "auto" : "1 / -1" }}>
                  <label style={estilos.inputLabel}>Dirección de entrega</label>
                  <input value={direccionEntrega} onChange={e => setDireccionEntrega(e.target.value)} style={estilos.input} placeholder="Av. ..." />
                </div>
              </div>
            </div>
          )}

          {/* Catálogo productos */}
          <div style={estilos.seccion}>
            <p style={estilos.seccionLabel}>Catálogo</p>

            {/* Filtro categorías */}
            {categorias.length > 1 && (
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
                {categorias.map((cat) => (
                  <button key={cat} onClick={() => setCategFiltro(cat)}
                    style={{
                      padding: "5px 12px", borderRadius: 20, border: "none", cursor: "pointer",
                      fontFamily: "'Lato',sans-serif", fontSize: 12, fontWeight: 600,
                      background: categFiltro === cat ? COLOR.verde : COLOR.verdePal,
                      color: categFiltro === cat ? "white" : COLOR.verde,
                      transition: "all 0.15s",
                      textTransform: cat === "todos" ? "none" : "capitalize",
                    }}>
                    {cat === "todos" ? "Todos" : cat === CATEG_PROMOS ? "Promociones" : cat}
                  </button>
                ))}
              </div>
            )}

            {/* Grid productos */}
            {productosFiltrados.length === 0 && promociones.length === 0 ? (
              <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13, color: "#999" }}>
                Sin productos cargados aún
              </p>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10 }}>
                {productosFiltrados.map((p) => (
                  <ProductoCard key={`prod-${p.id}`} item={p} esPromo={false} onClick={agregarItem} />
                ))}
                {promocionesFiltradas.map((p) => (
                  <ProductoCard key={`promo-${p.id}`} item={p} esPromo={true} onClick={agregarItem} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Panel derecho: orden ── */}
        <div style={{
          position: isMobile ? "static" : "sticky", top: isMobile ? undefined : 20,
          background: "white",
          border: `1.5px solid ${COLOR.borde}`, borderRadius: 14,
          boxShadow: "0 4px 20px rgba(44,85,69,0.08)", overflow: "hidden"
        }}>

          {/* Header panel */}
          <div style={{ background: COLOR.verde, padding: "14px 18px",
            display: "flex", alignItems: "center", gap: 8 }}>
            <ClipboardList size={16} color="white" />
            <span style={{ fontFamily: "'Playfair Display',Georgia,serif",
              fontSize: 15, fontWeight: 600, color: "white" }}>
              {tipoOrden === TIPO_ORDEN.MESA && mesaSeleccionada
                ? `Mesa ${mesaSeleccionada.numero}`
                : tipoOrden === TIPO_ORDEN.LLEVAR ? "Para llevar"
                : tipoOrden === TIPO_ORDEN.DELIVERY ? "Delivery"
                : "Nueva orden"}
            </span>
          </div>

          {/* Items */}
          <div style={{ padding: "12px 14px", minHeight: 200, maxHeight: isMobile ? "none" : 380, overflowY: isMobile ? "visible" : "auto" }}>
            {items.length === 0 ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center",
                justifyContent: "center", height: 160, gap: 8, color: "rgba(44,85,69,0.35)" }}>
                <ShoppingBag size={32} />
                <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13, margin: 0 }}>
                  Seleccioná productos del catálogo
                </p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {items.map((item) => (
                  <div key={item.key} style={{ display: "flex", alignItems: "center",
                    gap: 8, padding: "8px 0", borderBottom: `1px solid ${COLOR.borde}` }}>
                    <div style={{ flex: 1 }}>
                      {item.esPromo && (
                        <span style={{ fontSize: 9, fontWeight: 700, color: COLOR.dorado,
                          textTransform: "uppercase", letterSpacing: "0.06em" }}>Promo </span>
                      )}
                      <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
                        fontWeight: 600, color: COLOR.verde, margin: 0 }}>{item.nombre}</p>
                      <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                        color: "#888", margin: "2px 0 0 0" }}>
                        S/ {item.precio.toFixed(2)} × {item.cantidad}
                      </p>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <button onClick={() => cambiarCantidad(item.key, -1)} style={estilos.btnQty}>
                        <Minus size={12} />
                      </button>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
                        fontWeight: 700, color: COLOR.verde, minWidth: 20, textAlign: "center" }}>
                        {item.cantidad}
                      </span>
                      <button onClick={() => cambiarCantidad(item.key, 1)} style={estilos.btnQty}>
                        <Plus size={12} />
                      </button>
                      <button onClick={() => quitarItem(item.key)} style={estilos.btnDel}>
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {errForm.items && <p style={estilos.errorTxt}>{errForm.items}</p>}
          </div>

          {/* Footer panel */}
          <div style={{ borderTop: `1.5px solid ${COLOR.borde}`, padding: "12px 14px",
            display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                fontWeight: 700, color: "rgba(44,85,69,0.6)", textTransform: "uppercase",
                letterSpacing: "0.07em" }}>Total</span>
              <span style={{ fontFamily: "'Playfair Display',Georgia,serif",
                fontSize: 22, fontWeight: 700, color: COLOR.verde }}>
                S/ {total.toFixed(2)}
              </span>
            </div>
            {errForm.api && <p style={estilos.errorTxt}>{errForm.api}</p>}
            {exitoMsg && (
              <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                color: "#2e7d32", fontWeight: 600, margin: 0 }}>✓ {exitoMsg}</p>
            )}
            <button onClick={handleCrear} disabled={creando}
              style={{
                width: "100%", padding: "12px", borderRadius: 10, border: "none",
                background: creando ? "#aaa" : COLOR.verde, color: "white",
                fontFamily: "'Lato',sans-serif", fontSize: 14, fontWeight: 700,
                cursor: creando ? "not-allowed" : "pointer", transition: "background 0.15s",
              }}
              onMouseEnter={(e) => { if (!creando) e.currentTarget.style.background = COLOR.verdeOsc; }}
              onMouseLeave={(e) => { if (!creando) e.currentTarget.style.background = COLOR.verde; }}
            >
              {creando ? "Creando..." : "Crear orden"}
            </button>
            {items.length > 0 && (
              <button onClick={resetForm}
                style={{ width: "100%", padding: "8px", borderRadius: 8,
                  border: `1px solid ${COLOR.borde}`, background: "transparent",
                  fontFamily: "'Lato',sans-serif", fontSize: 12, fontWeight: 600,
                  color: "rgba(44,85,69,0.5)", cursor: "pointer" }}>
                Limpiar
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Tabla de órdenes ── */}
      <div style={{ background: "white", border: `1.5px solid ${COLOR.borde}`,
        borderRadius: 14, overflow: "hidden", boxShadow: "0 2px 10px rgba(44,85,69,0.06)" }}>
        <div style={{ padding: "14px 20px", borderBottom: `1px solid ${COLOR.borde}`,
          display: "flex", alignItems: "center", gap: 8 }}>
          <ClipboardList size={16} color={COLOR.verde} />
          <span style={{ fontFamily: "'Playfair Display',Georgia,serif",
            fontSize: 15, fontWeight: 600, color: COLOR.verde }}>
            Órdenes del día
          </span>
        </div>

        {ordenes.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center",
            fontFamily: "'Lato',sans-serif", fontSize: 13, color: "#999" }}>
            Sin órdenes registradas hoy
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 720 }}>
              <thead>
                <tr style={{ background: "rgba(44,85,69,0.04)" }}>
                  {[
                    { label: "#", cls: "" },
                    { label: "Tipo", cls: "" },
                    { label: "Mesa / Cliente", cls: "" },
                    { label: "Ítems", cls: "hidden sm:table-cell" },
                    { label: "Total", cls: "" },
                    { label: "Estado", cls: "" },
                    { label: "Hora", cls: "hidden sm:table-cell" },
                    { label: "Acciones", cls: "" },
                  ].map(({ label, cls }) => (
                    <th key={label} className={cls} style={{ padding: "10px 14px", textAlign: "left",
                      fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
                      color: "rgba(44,85,69,0.6)", textTransform: "uppercase",
                      letterSpacing: "0.07em", borderBottom: `1px solid ${COLOR.borde}` }}>
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ordenes.map((orden, idx) => (
                  <tr key={orden.id}
                    style={{ background: idx % 2 === 0 ? "white" : "rgba(44,85,69,0.015)",
                      borderBottom: `1px solid ${COLOR.borde}` }}>
                    <td style={estilos.td}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
                        fontWeight: 700, color: COLOR.verde }}>#{orden.id}</span>
                    </td>
                    <td style={estilos.td}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                        color: "#555" }}>{orden.tipo_orden_display || orden.tipo_orden}</span>
                    </td>
                    <td style={estilos.td}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 12, color: "#555" }}>
                        {orden.mesa_numero ? `Mesa ${orden.mesa_numero}`
                          : orden.cliente_nombre || orden.plataforma_delivery || "—"}
                      </span>
                    </td>
                    <td className="hidden sm:table-cell" style={estilos.td}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 12, color: "#555" }}>
                        {orden.detalles?.length || 0}
                      </span>
                    </td>
                    <td style={estilos.td}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
                        fontWeight: 700, color: COLOR.verde }}>
                        S/ {parseFloat(orden.total).toFixed(2)}
                      </span>
                    </td>
                    <td style={estilos.td}>
                      <StatusBadge estado={orden.estado} />
                    </td>
                    <td className="hidden sm:table-cell" style={estilos.td}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 11, color: "#888" }}>
                        {formatDateTime(orden.fecha_creacion)}
                      </span>
                    </td>
                    <td style={estilos.td}>
                      <div style={{ display: "flex", gap: 6 }}>
                        <button
                          onClick={() => abrirVer(orden)}
                          title="Ver detalle"
                          style={estilos.btnAccion("rgba(44,85,69,0.6)", "rgba(44,85,69,0.06)")}>
                          <Eye size={13} />
                        </button>
                        {orden.estado === "abierta" && (
                          <>
                            <button
                              onClick={() => window.open(`/comanda/${orden.id}`, "_blank")}
                              title="Ver comanda"
                              style={estilos.btnAccion(COLOR.verde, "rgba(44,85,69,0.08)")}>
                              <Printer size={13} />
                            </button>
                            <button
                              onClick={() => abrirEditar(orden)}
                              title="Editar orden"
                              style={estilos.btnAccion(COLOR.dorado, "rgba(201,168,76,0.12)")}>
                              <PenLine size={13} />
                            </button>
                            <button
                              onClick={() => setAnularTarget(orden)}
                              title="Anular orden"
                              style={estilos.btnAccion(COLOR.rojo, COLOR.rojoPal)}>
                              <Ban size={13} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Drawer editar orden ── */}
      {ordenEditar && (
        <div style={{
          position: "fixed", top: 0, right: 0, bottom: 0, width: drawerAncho,
          background: "white", boxShadow: "-4px 0 30px rgba(0,0,0,0.12)",
          zIndex: 1000, display: "flex", flexDirection: "column", overflowY: "auto",
        }}>
          {/* Header drawer */}
          <div style={{ background: COLOR.verde, padding: "14px 18px",
            display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <p style={{ fontFamily: "'Playfair Display',Georgia,serif", fontSize: 15,
                fontWeight: 600, color: "white", margin: 0 }}>
                {drawerModo === "ver" ? "Detalle" : "Editar"} Orden #{ordenEditar.id}
              </p>
              <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 11,
                color: "rgba(255,255,255,0.7)", margin: "2px 0 0 0" }}>
                {drawerModo === "ver"
                  ? `${ordenEditar.tipo_orden_display || ordenEditar.tipo_orden} · ${ordenEditar.estado}`
                  : "Agregá o quitá ítems de la orden"}
              </p>
            </div>
            <button onClick={() => setOrdenEditar(null)}
              style={{ background: "rgba(255,255,255,0.15)", border: "none",
                borderRadius: 8, padding: 6, cursor: "pointer", color: "white",
                display: "flex", alignItems: "center" }}>
              <X size={16} />
            </button>
          </div>

          {/* Info orden en modo ver */}
          {drawerModo === "ver" && (
            <div style={{ padding: "12px 16px", borderBottom: `1px solid ${COLOR.borde}`,
              background: "rgba(44,85,69,0.03)", display: "grid",
              gridTemplateColumns: "auto 1fr", gap: "4px 12px" }}>
              {ordenEditar.mesa_numero && (
                <>
                  <span style={estilos.infoDrawerLabel}>Mesa</span>
                  <span style={estilos.infoDrawerVal}>{ordenEditar.mesa_numero}</span>
                </>
              )}
              {ordenEditar.cliente_nombre && (
                <>
                  <span style={estilos.infoDrawerLabel}>Cliente</span>
                  <span style={estilos.infoDrawerVal}>{ordenEditar.cliente_nombre}</span>
                </>
              )}
              {ordenEditar.plataforma_delivery && (
                <>
                  <span style={estilos.infoDrawerLabel}>Plataforma</span>
                  <span style={estilos.infoDrawerVal}>{ordenEditar.plataforma_delivery}</span>
                </>
              )}
              {ordenEditar.direccion_entrega && (
                <>
                  <span style={estilos.infoDrawerLabel}>Dirección</span>
                  <span style={estilos.infoDrawerVal}>{ordenEditar.direccion_entrega}</span>
                </>
              )}
              <span style={estilos.infoDrawerLabel}>Mesero</span>
              <span style={estilos.infoDrawerVal}>{ordenEditar.usuario_nombre || "—"}</span>
              <span style={estilos.infoDrawerLabel}>Fecha</span>
              <span style={estilos.infoDrawerVal}>{formatDateTime(ordenEditar.fecha_creacion)}</span>
            </div>
          )}

          {/* Ítems actuales */}
          <div style={{ padding: "14px 16px", borderBottom: `1px solid ${COLOR.borde}` }}>
            <p style={estilos.seccionLabel}>Ítems actuales</p>
            {ordenEditar.detalles?.length === 0 ? (
              <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 12, color: "#999" }}>Sin ítems</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {ordenEditar.detalles?.map((d) => (
                  <div key={d.id} style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "center", padding: "6px 0",
                    borderBottom: `1px solid ${COLOR.borde}` }}>
                    <div style={{ flex: 1 }}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                        fontWeight: 600, color: COLOR.verde }}>
                        {d.cantidad}× {d.producto?.nombre || d.promocion?.nombre || `Ítem #${d.id}`}
                      </span>
                      {d.impreso && (
                        <span style={{ marginLeft: 6, fontSize: 10, color: "#2e7d32",
                          fontWeight: 700 }}>✓ enviado</span>
                      )}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 12, color: "#888" }}>
                        S/ {parseFloat(d.subtotal || 0).toFixed(2)}
                      </span>
                      <button
                        onClick={() => handleEliminarDetalle(d.id, d.impreso)}
                        title="Quitar ítem"
                        style={{ ...estilos.btnDel, width: 26, height: 26 }}>
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Catálogo para agregar — solo en modo editar */}
          <div style={{ padding: "14px 16px", flex: 1, display: drawerModo === "ver" ? "none" : "block" }}>
            <p style={estilos.seccionLabel}>Agregar productos</p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
              {productos.map((prod) => (
                <ProductoCard key={`ep-${prod.id}`} item={prod} esPromo={false}
                  onClick={agregarItemEditar} />
              ))}
              {promociones.map((promo) => (
                <ProductoCard key={`epr-${promo.id}`} item={promo} esPromo={true}
                  onClick={agregarItemEditar} />
              ))}
            </div>

            {/* Items a agregar */}
            {itemsEditar.length > 0 && (
              <div style={{ background: COLOR.verdePal, borderRadius: 10,
                padding: "12px 14px", marginTop: 8 }}>
                <p style={{ ...estilos.seccionLabel, marginBottom: 8 }}>Por agregar</p>
                {itemsEditar.map((item) => (
                  <div key={item.key} style={{ display: "flex", alignItems: "center",
                    gap: 8, marginBottom: 8 }}>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                        fontWeight: 600, color: COLOR.verde, margin: 0 }}>{item.nombre}</p>
                    </div>
                    <button onClick={() => cambiarCantidadEditar(item.key, -1)} style={estilos.btnQty}>
                      <Minus size={11} />
                    </button>
                    <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 13,
                      fontWeight: 700, color: COLOR.verde, minWidth: 18, textAlign: "center" }}>
                      {item.cantidad}
                    </span>
                    <button onClick={() => cambiarCantidadEditar(item.key, 1)} style={estilos.btnQty}>
                      <Plus size={11} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer drawer — solo en modo editar */}
          <div style={{ padding: "14px 16px", borderTop: `1.5px solid ${COLOR.borde}`,
            display: drawerModo === "ver" ? "none" : "flex", flexDirection: "column", gap: 8 }}>
            {editExito && (
              <p style={{ fontFamily: "'Lato',sans-serif", fontSize: 12,
                color: "#2e7d32", fontWeight: 600, margin: "0 0 8px 0" }}>✓ {editExito}</p>
            )}
            <button onClick={handleConfirmarEditar}
              disabled={agregando || itemsEditar.length === 0}
              style={{
                width: "100%", padding: 12, borderRadius: 10, border: "none",
                background: (agregando || itemsEditar.length === 0) ? "#aaa" : COLOR.verde,
                color: "white", fontFamily: "'Lato',sans-serif", fontSize: 14,
                fontWeight: 700, cursor: (agregando || itemsEditar.length === 0) ? "not-allowed" : "pointer",
              }}>
              {agregando ? "Agregando..." : `Agregar ${itemsEditar.length > 0 ? `(${itemsEditar.reduce((s,i)=>s+i.cantidad,0)} ítems)` : "ítems"}`}
            </button>
          </div>
        </div>
      )}

      {/* Total en modo ver */}
      {ordenEditar && drawerModo === "ver" && (
        <div style={{ position: "fixed", bottom: 0, right: 0, width: drawerAncho,
          padding: "14px 18px", background: "white",
          borderTop: `2px solid ${COLOR.borde}`, zIndex: 1001,
          display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
            color: "rgba(44,85,69,0.6)", textTransform: "uppercase", letterSpacing: "0.07em" }}>
            Total
          </span>
          <span style={{ fontFamily: "'Playfair Display',Georgia,serif",
            fontSize: 22, fontWeight: 700, color: COLOR.verde }}>
            S/ {parseFloat(ordenEditar.total).toFixed(2)}
          </span>
        </div>
      )}

      {/* Overlay drawer */}
      {ordenEditar && (
        <div onClick={() => setOrdenEditar(null)}
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)", zIndex: 999 }} />
      )}

      {/* ── Confirm anular ── */}
      <ConfirmDialog
        abierto={!!anularTarget}
        titulo="¿Anular orden?"
        descripcion={`La orden #${anularTarget?.id} será anulada. Esta acción no se puede deshacer.`}
        textoOk="Anular"
        variante="danger"
        cargando={anulando}
        onConfirmar={handleAnular}
        onCancelar={() => setAnularTarget(null)}
      />
    </div>
  );
}

const estilos = {
  seccion:      { background: "white", border: `1.5px solid rgba(44,85,69,0.12)`,
    borderRadius: 12, padding: "16px 18px" },
  seccionLabel: { fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
    color: "rgba(44,85,69,0.6)", textTransform: "uppercase", letterSpacing: "0.07em",
    margin: "0 0 12px 0" },
  inputLabel:   { fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
    color: "rgba(44,85,69,0.75)", textTransform: "uppercase", letterSpacing: "0.07em",
    display: "block", marginBottom: 5 },
  input:        { width: "100%", padding: "9px 12px", borderRadius: 8,
    border: "1px solid rgba(44,85,69,0.2)", fontFamily: "'Lato',sans-serif",
    fontSize: 13.5, color: "#333", outline: "none", boxSizing: "border-box" },
  select:       { width: "100%", padding: "9px 12px", borderRadius: 8,
    border: "1px solid rgba(44,85,69,0.2)", fontFamily: "'Lato',sans-serif",
    fontSize: 13.5, color: "#333", outline: "none", boxSizing: "border-box",
    cursor: "pointer" },
  errorTxt:     { fontFamily: "'Lato',sans-serif", fontSize: 11.5, color: "#c62828", margin: "4px 0 0 0" },
  statPill:     { display: "flex", alignItems: "center", gap: 6, padding: "6px 12px",
    background: "rgba(44,85,69,0.08)", borderRadius: 20,
    fontFamily: "'Lato',sans-serif", fontSize: 12, fontWeight: 600, color: "rgba(44,85,69,0.8)" },
  btnQty:       { width: 24, height: 24, borderRadius: 6, border: "1px solid rgba(44,85,69,0.2)",
    background: "white", cursor: "pointer", display: "flex", alignItems: "center",
    justifyContent: "center", color: "#2C5545" },
  btnDel:       { width: 24, height: 24, borderRadius: 6, border: "none",
    background: "rgba(212,24,61,0.08)", cursor: "pointer", display: "flex",
    alignItems: "center", justifyContent: "center", color: "#d4183d" },
  btnAccion:    (color, bg) => ({
    width: 30, height: 30, borderRadius: 7, border: "none", cursor: "pointer",
    background: bg, color, display: "flex", alignItems: "center", justifyContent: "center",
  }),
  td:           { padding: "10px 14px", verticalAlign: "middle" },
  infoDrawerLabel: { fontFamily: "'Lato',sans-serif", fontSize: 11, fontWeight: 700,
    color: "rgba(44,85,69,0.6)", textTransform: "uppercase", letterSpacing: "0.06em",
    whiteSpace: "nowrap" },
  infoDrawerVal:   { fontFamily: "'Lato',sans-serif", fontSize: 12, color: "#333" },
};

import { useState, useEffect } from "react";
import InputField from "../../components/common/InputField";

export default function OrdenForm({ 
  onSubmit, 
  onSetSubmit,
  cargando = false, 
  mesas = [], 
  productos = [], 
  promociones = []
}) {
  const [tipoOrden, setTipoOrden] = useState("mesa");
  const [mesaId, setMesaId] = useState("");
  const [detalles, setDetalles] = useState([]);
  const [nuevoDetalle, setNuevoDetalle] = useState({
    producto_id: "",
    promocion_id: "",
    cantidad: 1,
    nota: "",
  });
  const [errores, setErrores] = useState({});

  const total = detalles.reduce((sum, item) => {
    let precio = 0;
    if (item.producto_id) {
      const prod = productos.find((p) => p.id === parseInt(item.producto_id));
      if (prod) precio += parseFloat(prod.precio);
    }
    if (item.promocion_id) {
      const promo = promociones.find((p) => p.id === parseInt(item.promocion_id));
      if (promo) precio += parseFloat(promo.precio);
    }
    return sum + precio * item.cantidad;
  }, 0);

  const validarDetalle = () => {
    const newErrores = {};
    if (!nuevoDetalle.producto_id && !nuevoDetalle.promocion_id) {
      newErrores.item = "Debe seleccionar al menos un producto o promoción";
    }
    if (nuevoDetalle.cantidad <= 0) {
      newErrores.cantidad = "La cantidad debe ser mayor a 0";
    }
    return newErrores;
  };

  const agregarDetalle = () => {
    const detalleErrores = validarDetalle();
    if (Object.keys(detalleErrores).length > 0) {
      setErrores(detalleErrores);
      return;
    }
    setErrores({});
    setDetalles([...detalles, { ...nuevoDetalle, id: Date.now() }]);
    setNuevoDetalle({ producto_id: "", promocion_id: "", cantidad: 1, nota: "" });
  };

  const eliminarDetalle = (id) => {
    setDetalles(detalles.filter((d) => d.id !== id));
  };

  const validarFormulario = () => {
    const newErrores = {};
    if (tipoOrden === "mesa" && !mesaId) {
      newErrores.mesa = "Debe seleccionar una mesa";
    }
    if (detalles.length === 0) {
      newErrores.detalles = "La orden debe tener al menos un ítem";
    }
    return newErrores;
  };

  const ejecutarSubmit = async () => {
    const formErrores = validarFormulario();
    if (Object.keys(formErrores).length > 0) {
      setErrores(formErrores);
      return;
    }
    setErrores({});
    await onSubmit({ tipoOrden, mesaId: tipoOrden === "mesa" ? parseInt(mesaId) : null, detalles });
  };

  // Pasar la función de submit al padre cuando se monta
  useEffect(() => {
    if (onSetSubmit) {
      onSetSubmit(ejecutarSubmit);
    }
  }, [onSetSubmit, tipoOrden, mesaId, detalles, onSubmit]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Tipo de orden */}
      <div>
        <label
          style={{
            fontFamily: "'Lato', sans-serif",
            fontSize: "11px",
            fontWeight: 700,
            color: "rgba(44,85,69,0.75)",
            letterSpacing: "0.07em",
            textTransform: "uppercase",
          }}
        >
          Tipo de Orden *
        </label>
        <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
          {[
            { value: "mesa", label: "Mesa" },
            { value: "llevar", label: "Para llevar" },
          ].map((op) => (
            <label
              key={op.value}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                fontFamily: "'Lato', sans-serif",
                fontSize: "13px",
              }}
            >
              <input
                type="radio"
                value={op.value}
                checked={tipoOrden === op.value}
                onChange={(e) => setTipoOrden(e.target.value)}
                style={{ cursor: "pointer" }}
              />
              {op.label}
            </label>
          ))}
        </div>
      </div>

      {/* Selección de mesa (solo si es tipo mesa) */}
      {tipoOrden === "mesa" && (
        <InputField
          label="Seleccionar Mesa"
          type="select"
          options={mesas.map((m) => ({ value: m.id, label: `Mesa ${m.numero}` }))}
          value={mesaId}
          onChange={setMesaId}
          error={errores.mesa}
          required
        />
      )}

      {/* Agregar ítems */}
      <div
        style={{
          padding: "16px",
          backgroundColor: "rgba(44,85,69,0.03)",
          borderRadius: "8px",
          border: "1px dashed rgba(44,85,69,0.2)",
        }}
      >
        <h4
          style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: "14px",
            fontWeight: 600,
            color: "#2C5545",
            margin: "0 0 12px 0",
          }}
        >
          Agregar Ítems
        </h4>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <InputField
            label="Producto"
            type="select"
            options={productos.map((p) => ({ value: p.id, label: p.nombre }))}
            value={nuevoDetalle.producto_id}
            onChange={(val) => setNuevoDetalle({ ...nuevoDetalle, producto_id: val })}
          />

          <InputField
            label="Promoción"
            type="select"
            options={promociones.map((p) => ({ value: p.id, label: p.nombre }))}
            value={nuevoDetalle.promocion_id}
            onChange={(val) => setNuevoDetalle({ ...nuevoDetalle, promocion_id: val })}
          />

          {errores.item && (
            <p style={{ fontFamily: "'Lato', sans-serif", fontSize: "11.5px", color: "#c62828", margin: 0 }}>
              {errores.item}
            </p>
          )}

          <InputField
            label="Cantidad"
            type="number"
            value={nuevoDetalle.cantidad}
            onChange={(val) => setNuevoDetalle({ ...nuevoDetalle, cantidad: parseInt(val) || 1 })}
            error={errores.cantidad}
          />

          <InputField
            label="Nota (opcional)"
            type="text"
            placeholder="Ej: Sin picante, sin cebolla..."
            value={nuevoDetalle.nota}
            onChange={(val) => setNuevoDetalle({ ...nuevoDetalle, nota: val })}
          />

          <button
            onClick={agregarDetalle}
            style={{
              padding: "10px",
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
            + Agregar Ítem
          </button>
        </div>
      </div>

      {/* Lista de ítems */}
      {detalles.length > 0 && (
        <div
          style={{
            padding: "16px",
            backgroundColor: "rgba(44,85,69,0.02)",
            borderRadius: "8px",
            border: "1px solid rgba(44,85,69,0.1)",
          }}
        >
          <h4
            style={{
              fontFamily: "'Playfair Display', Georgia, serif",
              fontSize: "14px",
              fontWeight: 600,
              color: "#2C5545",
              margin: "0 0 12px 0",
            }}
          >
            Ítems de la Orden ({detalles.length})
          </h4>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {detalles.map((detalle) => {
              const prod = productos.find((p) => p.id === parseInt(detalle.producto_id));
              const promo = promociones.find((p) => p.id === parseInt(detalle.promocion_id));
              const precioUnitario = (parseFloat(prod?.precio || 0) + parseFloat(promo?.precio || 0)).toFixed(2);
              const subtotal = (precioUnitario * detalle.cantidad).toFixed(2);

              return (
                <div
                  key={detalle.id}
                  style={{
                    padding: "12px",
                    backgroundColor: "white",
                    borderRadius: "6px",
                    border: "1px solid rgba(44,85,69,0.1)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <p
                      style={{
                        fontFamily: "'Lato', sans-serif",
                        fontSize: "13px",
                        fontWeight: 600,
                        color: "#2C5545",
                        margin: "0 0 4px 0",
                      }}
                    >
                      {detalle.cantidad}x {prod?.nombre || promo?.nombre || "Item"}
                    </p>
                    {detalle.nota && (
                      <p
                        style={{
                          fontFamily: "'Lato', sans-serif",
                          fontSize: "11px",
                          color: "#999",
                          margin: "0 0 4px 0",
                        }}
                      >
                        📝 {detalle.nota}
                      </p>
                    )}
                    <p
                      style={{
                        fontFamily: "'Lato', sans-serif",
                        fontSize: "11px",
                        color: "#666",
                        margin: 0,
                      }}
                    >
                      ${precioUnitario} × {detalle.cantidad} = <strong>${subtotal}</strong>
                    </p>
                  </div>
                  <button
                    onClick={() => eliminarDetalle(detalle.id)}
                    style={{
                      padding: "6px 10px",
                      borderRadius: "6px",
                      border: "1px solid #f5bfb7",
                      backgroundColor: "#fdecea",
                      color: "#c62828",
                      fontFamily: "'Lato', sans-serif",
                      fontSize: "12px",
                      fontWeight: 600,
                      cursor: "pointer",
                      transition: "all 0.2s",
                      marginLeft: "12px",
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = "#fcccc6";
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = "#fdecea";
                    }}
                  >
                    Quitar
                  </button>
                </div>
              );
            })}
          </div>

          {errores.detalles && (
            <p style={{ fontFamily: "'Lato', sans-serif", fontSize: "11.5px", color: "#c62828", margin: "12px 0 0 0" }}>
              {errores.detalles}
            </p>
          )}
        </div>
      )}

      {/* Total */}
      <div
        style={{
          padding: "16px",
          backgroundColor: "rgba(44,85,69,0.05)",
          borderRadius: "8px",
          border: "2px solid rgba(44,85,69,0.2)",
          textAlign: "right",
        }}
      >
        <p
          style={{
            fontFamily: "'Lato', sans-serif",
            fontSize: "11px",
            fontWeight: 700,
            color: "rgba(44,85,69,0.7)",
            margin: "0 0 6px 0",
            textTransform: "uppercase",
            letterSpacing: "0.07em",
          }}
        >
          Total
        </p>
        <p
          style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: "28px",
            fontWeight: 600,
            color: "#2C5545",
            margin: 0,
          }}
        >
          ${total.toFixed(2)}
        </p>
      </div>
    </div>
  );
}

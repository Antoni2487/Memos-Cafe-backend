import { useState, useEffect } from "react";
import { FormModal, InputField } from "../common";

export default function PromocionForm({ abierto, promocion, onGuardar, onCerrar, cargando }) {
  const hoy = new Date().toISOString().split("T")[0];

  const [form, setForm] = useState({
    nombre: "", descripcion: "", precio: "",
    imagen_url: "", fecha_inicio: hoy, fecha_fin: "",
  });
  const [errores, setErrores] = useState({});

  useEffect(() => {
    if (promocion) {
      setForm({
        nombre:       promocion.nombre       || "",
        descripcion:  promocion.descripcion  || "",
        precio:       promocion.precio       || "",
        imagen_url:   promocion.imagen_url   || "",
        fecha_inicio: promocion.fecha_inicio || hoy,
        fecha_fin:    promocion.fecha_fin    || "",
      });
    } else {
      setForm({ nombre: "", descripcion: "", precio: "", imagen_url: "", fecha_inicio: hoy, fecha_fin: "" });
    }
    setErrores({});
  }, [promocion, abierto]);

  const set = (campo) => (val) => setForm((f) => ({ ...f, [campo]: val }));

  const validar = () => {
    const e = {};
    if (!form.nombre.trim())        e.nombre      = "El nombre es obligatorio";
    if (!form.precio)               e.precio      = "El precio es obligatorio";
    if (Number(form.precio) <= 0)   e.precio      = "El precio debe ser mayor a 0";
    if (!form.fecha_inicio)         e.fecha_inicio = "La fecha de inicio es obligatoria";
    if (!form.fecha_fin)            e.fecha_fin    = "La fecha de fin es obligatoria";
    if (form.fecha_inicio && form.fecha_fin && form.fecha_fin < form.fecha_inicio)
      e.fecha_fin = "La fecha de fin no puede ser anterior a la de inicio";
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const handleGuardar = () => {
    if (!validar()) return;
    onGuardar({ ...form, precio: Number(form.precio) });
  };

  return (
    <FormModal
      abierto={abierto}
      titulo={promocion ? "Editar Promoción" : "Nueva Promoción"}
      onCerrar={onCerrar}
      onGuardar={handleGuardar}
      cargando={cargando}
      textoGuardar={promocion ? "Guardar cambios" : "Crear promoción"}
      maxWidth="520px"
    >
      <InputField label="Nombre" value={form.nombre} onChange={set("nombre")}
        placeholder="Ej: Combo del día" required error={errores.nombre} />
      <InputField label="Descripción" value={form.descripcion} onChange={set("descripcion")}
        placeholder="Descripción opcional" rows={3} />
      <InputField label="Precio (S/)" type="number" value={form.precio} onChange={set("precio")}
        placeholder="0.00" required error={errores.precio} />
      <InputField label="URL de imagen" value={form.imagen_url} onChange={set("imagen_url")}
        placeholder="https://..." />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <InputField label="Fecha inicio" type="date" value={form.fecha_inicio}
          onChange={set("fecha_inicio")} required error={errores.fecha_inicio} />
        <InputField label="Fecha fin" type="date" value={form.fecha_fin}
          onChange={set("fecha_fin")} required error={errores.fecha_fin} />
      </div>
    </FormModal>
  );
}
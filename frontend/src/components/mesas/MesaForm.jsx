import { useState, useEffect } from "react";
import { FormModal, InputField } from "../common";

export default function MesaForm({ abierto, mesa, onGuardar, onCerrar, cargando }) {
  const [form, setForm] = useState({ numero: "", capacidad: "" });
  const [errores, setErrores] = useState({});

  useEffect(() => {
    if (mesa) {
      setForm({
        numero: mesa.numero || "",
        capacidad: mesa.capacidad || "",
      });
    } else {
      setForm({ numero: "", capacidad: "" });
    }
    setErrores({});
  }, [mesa, abierto]);

  const set = (campo) => (val) => setForm((f) => ({ ...f, [campo]: val }));

  const validar = () => {
    const e = {};
    if (!form.numero) e.numero = "El número es obligatorio";
    if (Number(form.numero) <= 0) e.numero = "El número debe ser mayor a 0";
    if (!form.capacidad) e.capacidad = "La capacidad es obligatoria";
    if (Number(form.capacidad) <= 0) e.capacidad = "La capacidad debe ser mayor a 0";
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const handleGuardar = () => {
    if (!validar()) return;
    onGuardar({
      numero: Number(form.numero),
      capacidad: Number(form.capacidad),
    });
  };

  return (
    <FormModal
      abierto={abierto}
      titulo={mesa ? "Editar Mesa" : "Nueva Mesa"}
      onCerrar={onCerrar}
      onGuardar={handleGuardar}
      cargando={cargando}
      textoGuardar={mesa ? "Guardar cambios" : "Crear mesa"}
      maxWidth="420px"
    >
      <InputField
        label="Número de mesa"
        type="number"
        value={form.numero}
        onChange={set("numero")}
        placeholder="Ej: 5"
        required
        error={errores.numero}
      />
      <InputField
        label="Capacidad (personas)"
        type="number"
        value={form.capacidad}
        onChange={set("capacidad")}
        placeholder="Ej: 4"
        required
        error={errores.capacidad}
      />
    </FormModal>
  );
}
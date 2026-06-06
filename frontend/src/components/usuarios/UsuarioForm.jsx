import { useState, useEffect } from "react";
import { FormModal, InputField } from "../common";
import { ROLES } from "../../utils/constants";

const ROLES_OPTIONS = [
  { value: ROLES.ADMIN,   label: "Admin" },
  { value: ROLES.CAJERO,  label: "Cajero" },
  { value: ROLES.MESERO,  label: "Mesero" },
];

export default function UsuarioForm({ abierto, usuario, onGuardar, onCerrar, cargando }) {
  const [form, setForm] = useState({ name: "", email: "", password: "", group_name: "" });
  const [errores, setErrores] = useState({});

  useEffect(() => {
    if (usuario) {
      setForm({
        name: usuario.name || "",
        email: usuario.email,
        password: "",
        group_name: usuario.groups?.[0]?.name ?? "",
      });
    } else {
      setForm({ name: "", email: "", password: "", group_name: "" });
    }
    setErrores({});
  }, [usuario, abierto]);

  const set = (campo) => (val) => setForm((f) => ({ ...f, [campo]: val }));

  const validar = () => {
    const e = {};
    if (!form.email) e.email = "El email es obligatorio";
    if (!usuario && !form.password) e.password = "La contraseña es obligatoria";
    if (form.password && form.password.length < 8) e.password = "Mínimo 8 caracteres";
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const handleGuardar = () => {
    if (!validar()) return;
    const datos = { name: form.name, email: form.email, group_name: form.group_name };
    if (form.password) datos.password = form.password;
    onGuardar(datos);
  };

  return (
    <FormModal
      abierto={abierto}
      titulo={usuario ? "Editar Usuario" : "Nuevo Usuario"}
      onCerrar={onCerrar}
      onGuardar={handleGuardar}
      cargando={cargando}
      textoGuardar={usuario ? "Guardar cambios" : "Crear usuario"}
    >
      <InputField
        label="Nombre"
        value={form.name}
        onChange={set("name")}
        placeholder="Nombre completo"
        error={errores.name}
      />
      <InputField
        label="Email"
        type="email"
        value={form.email}
        onChange={set("email")}
        placeholder="correo@ejemplo.com"
        required
        error={errores.email}
      />
      <InputField
        label={usuario ? "Nueva contraseña (opcional)" : "Contraseña"}
        type="password"
        value={form.password}
        onChange={set("password")}
        placeholder="••••••••"
        required={!usuario}
        error={errores.password}
      />
      <InputField
        label="Rol"
        value={form.group_name}
        onChange={set("group_name")}
        options={ROLES_OPTIONS}
      />
    </FormModal>
  );
}

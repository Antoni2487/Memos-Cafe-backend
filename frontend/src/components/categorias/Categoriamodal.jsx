import { useState } from "react";
import { X, Tag } from "lucide-react";
import categoriaService from "../../services/categoriaService";
 
/**
 * Props:
 *   onClose  () => void
 *   onSave   (categoria: { id, nombre, activo }) => void  ← objeto del backend
 */
export function CategoryModal({ onClose, onSave }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
 
  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = name.trim();
 
    // Validación cliente
    if (!trimmed) {
      setError("El nombre de la categoría es obligatorio.");
      return;
    }
    if (trimmed.length < 2) {
      setError("El nombre debe tener al menos 2 caracteres.");
      return;
    }
 
    setLoading(true);
    setError("");
    try {
      const nueva = await categoriaService.crear(trimmed);
      onSave(nueva); // { id, nombre, activo: true }
    } catch (err) {
      // El backend devuelve "Ya existe una categoría con el nombre '...'"
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
 
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.35)", backdropFilter: "blur(2px)" }}
    >
      <div
        style={{
          backgroundColor: "#F8F4EE",
          borderRadius: "12px",
          boxShadow: "0 20px 60px rgba(44,85,69,0.18), 0 4px 16px rgba(0,0,0,0.08)",
          width: "420px",
          maxWidth: "calc(100vw - 32px)",
        }}
      >
        {/* Header */}
        <div
          style={{
            borderBottom: "1px solid rgba(44,85,69,0.12)",
            padding: "20px 24px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div className="flex items-center gap-3">
            <div
              style={{ backgroundColor: "rgba(201,168,76,0.15)", borderRadius: "8px" }}
              className="w-9 h-9 flex items-center justify-center"
            >
              <Tag size={18} style={{ color: "#C9A84C" }} />
            </div>
            <h2
              style={{
                fontFamily: "'Playfair Display', serif",
                color: "#2C5545",
                fontSize: "18px",
                fontWeight: 600,
              }}
            >
              Nueva Categoría
            </h2>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            style={{ color: "rgba(44,85,69,0.45)", borderRadius: "6px" }}
            className="w-8 h-8 flex items-center justify-center hover:bg-teal-50 transition-colors"
          >
            <X size={18} />
          </button>
        </div>
 
        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-5">
            <label
              style={{
                fontFamily: "'Lato', sans-serif",
                color: "#2C5545",
                fontSize: "13px",
                fontWeight: 600,
                letterSpacing: "0.5px",
                textTransform: "uppercase",
                display: "block",
                marginBottom: "6px",
              }}
            >
              Nombre de la categoría
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (error) setError("");
              }}
              placeholder="Ej: Bebidas frías, Postres, Entradas…"
              disabled={loading}
              style={{
                fontFamily: "'Lato', sans-serif",
                width: "100%",
                padding: "10px 14px",
                borderRadius: "8px",
                border: error
                  ? "1.5px solid #d4183d"
                  : "1.5px solid rgba(44,85,69,0.25)",
                backgroundColor: loading ? "rgba(44,85,69,0.04)" : "#fff",
                color: "#2C5545",
                fontSize: "14px",
                outline: "none",
                transition: "border-color 0.15s",
                cursor: loading ? "not-allowed" : "text",
              }}
              onFocus={(e) => {
                if (!error) e.target.style.borderColor = "#C9A84C";
              }}
              onBlur={(e) => {
                if (!error) e.target.style.borderColor = "rgba(44,85,69,0.25)";
              }}
              autoFocus
            />
            {error && (
              <p
                style={{
                  fontFamily: "'Lato', sans-serif",
                  color: "#d4183d",
                  fontSize: "12px",
                  marginTop: "5px",
                }}
              >
                {error}
              </p>
            )}
            <p
              style={{
                fontFamily: "'Lato', sans-serif",
                color: "rgba(44,85,69,0.5)",
                fontSize: "12px",
                marginTop: "6px",
              }}
            >
              La categoría se creará como activa por defecto.
            </p>
          </div>
 
          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              style={{
                fontFamily: "'Lato', sans-serif",
                color: "#2C5545",
                border: "1.5px solid rgba(44,85,69,0.3)",
                borderRadius: "8px",
                padding: "9px 20px",
                fontSize: "14px",
                backgroundColor: "transparent",
                cursor: loading ? "not-allowed" : "pointer",
                opacity: loading ? 0.5 : 1,
                transition: "all 0.15s",
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = "rgba(44,85,69,0.06)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                fontFamily: "'Lato', sans-serif",
                backgroundColor: loading ? "rgba(44,85,69,0.5)" : "#2C5545",
                color: "#F8F4EE",
                borderRadius: "8px",
                padding: "9px 20px",
                fontSize: "14px",
                border: "none",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "background-color 0.15s",
                minWidth: "140px",
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = "#234438";
              }}
              onMouseLeave={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = "#2C5545";
              }}
            >
              {loading ? "Creando…" : "Crear categoría"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
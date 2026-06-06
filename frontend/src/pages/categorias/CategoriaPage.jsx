import { useState, useMemo, useEffect, useCallback } from "react";
import { Tag, Plus } from "lucide-react";
import categoriaService from "../../services/categoriaService";
import { PageHeader } from "../common/PageHeader";
import { StatCard } from "../common/SearchBar-StatCard";
import { SearchBar } from "../common/SearchBar-StatCard";
import { DataTable } from "../common/DataTable";
import { StatusBadge } from "../common/StatusBadge";
import { LoadingSpinner, EmptyState } from "../common/LoadingSpinner-EmptyState";
import { ConfirmModal } from "../common/Modals";
import { CategoryModal } from "./CategoryModal";

export default function CategoriasPage() {
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState(null); 
  const [deactivating, setDeactivating] = useState(false);
  const [deactivateError, setDeactivateError] = useState(null);

  const cargarCategorias = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await categoriaService.listar();
      setCategorias(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);
 
  useEffect(() => {
    cargarCategorias();
  }, [cargarCategorias]);
 
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return categorias;
    return categorias.filter((c) => c.nombre.toLowerCase().includes(q));
  }, [categorias, search]);
 
  const activeCount = categorias.filter((c) => c.activo).length;
  const inactiveCount = categorias.filter((c) => !c.activo).length;
  const handleCreated = (nueva) => {
    setCategorias((prev) => [nueva, ...prev]);
    setShowCreateModal(false);
  };
 
  const handleDeactivateRequest = (cat) => {
    setDeactivateError(null);
    setConfirmTarget(cat);
  };
 
  const handleConfirmDeactivate = async () => {
    if (!confirmTarget) return;
    setDeactivating(true);
    setDeactivateError(null);
    try {
      const updated = await categoriaService.desactivar(confirmTarget.id);
      setCategorias((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );
      setConfirmTarget(null);
    } catch (err) {
      // El backend puede responder "tiene productos disponibles"
      setDeactivateError(err.message);
    } finally {
      setDeactivating(false);
    }
  };
 
  // ── Columnas de la DataTable ────────────────────────────────────────────────
  const columns = [
    {
      key: "nombre",
      header: "Nombre",
      render: (cat) => (
        <div className="flex items-center gap-3">
          <div
            style={{
              backgroundColor: cat.activo
                ? "rgba(201,168,76,0.15)"
                : "rgba(0,0,0,0.06)",
              borderRadius: "7px",
              width: "34px",
              height: "34px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <Tag
              size={15}
              style={{ color: cat.activo ? "#C9A84C" : "rgba(44,85,69,0.3)" }}
            />
          </div>
          <span
            style={{
              fontFamily: "'Lato', sans-serif",
              color: cat.activo ? "#2C5545" : "rgba(44,85,69,0.4)",
              fontSize: "15px",
              fontWeight: 500,
              textDecoration: cat.activo ? "none" : "line-through",
            }}
          >
            {cat.nombre}
          </span>
        </div>
      ),
    },
    {
      key: "activo",
      header: "Estado",
      render: (cat) => (
        <StatusBadge active={cat.activo} />
      ),
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (cat) =>
        cat.activo ? (
          <button
            onClick={() => handleDeactivateRequest(cat)}
            style={{
              fontFamily: "'Lato', sans-serif",
              fontSize: "13px",
              color: "#d4183d",
              backgroundColor: "rgba(212,24,61,0.07)",
              border: "none",
              borderRadius: "6px",
              padding: "6px 14px",
              cursor: "pointer",
              fontWeight: 500,
              transition: "background-color 0.15s",
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.backgroundColor = "rgba(212,24,61,0.14)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = "rgba(212,24,61,0.07)")
            }
          >
            Desactivar
          </button>
        ) : (
          <span
            style={{
              fontFamily: "'Lato', sans-serif",
              fontSize: "12px",
              color: "rgba(44,85,69,0.35)",
              fontStyle: "italic",
            }}
          >
            Inactiva
          </span>
        ),
    },
  ];
 
  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div
      className="flex-1 overflow-y-auto"
      style={{ backgroundColor: "#F8F4EE" }}
    >
      {/* Watermark decorativo */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          zIndex: 0,
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='600' viewBox='0 0 600 600'%3E%3Cg fill='none' stroke='%232C5545' stroke-width='1' opacity='0.07'%3E%3Cellipse cx='300' cy='300' rx='180' ry='280' transform='rotate(-30 300 300)'/%3E%3Cellipse cx='300' cy='300' rx='160' ry='260' transform='rotate(10 300 300)'/%3E%3Cellipse cx='300' cy='300' rx='140' ry='240' transform='rotate(50 300 300)'/%3E%3Cpath d='M300 50 Q340 150 300 300 Q260 150 300 50'/%3E%3Cpath d='M300 550 Q340 450 300 300 Q260 450 300 550'/%3E%3C/g%3E%3C/svg%3E")`,
          backgroundSize: "520px",
          backgroundPosition: "right -60px top -40px",
          backgroundRepeat: "no-repeat",
          opacity: 0.5,
        }}
      />
 
      <div style={{ position: "relative", zIndex: 1, padding: "32px 36px 48px" }}>
 
        {/* Header de página */}
        <PageHeader
          title="Categorías"
          subtitle="Organiza el menú agrupando los productos por categoría"
        />
 
        {/* Stats */}
        <div className="flex gap-4 mb-8 mt-6">
          <StatCard label="Total categorías" value={categorias.length} />
          <StatCard label="Activas" value={activeCount} accent />
          <StatCard label="Inactivas" value={inactiveCount} />
        </div>
 
        {/* Toolbar: búsqueda + botón crear */}
        <div
          style={{
            backgroundColor: "#fff",
            borderRadius: "10px",
            boxShadow: "0 2px 10px rgba(44,85,69,0.08)",
            padding: "18px 22px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "16px",
            marginBottom: "20px",
          }}
        >
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Buscar por nombre…"
          />
          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              fontFamily: "'Lato', sans-serif",
              backgroundColor: "#2C5545",
              color: "#F8F4EE",
              borderRadius: "8px",
              padding: "9px 20px",
              fontSize: "14px",
              fontWeight: 600,
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              whiteSpace: "nowrap",
              transition: "background-color 0.15s",
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.backgroundColor = "#234438")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = "#2C5545")
            }
          >
            <Plus size={16} />
            Nueva categoría
          </button>
        </div>
 
        {/* Cuerpo principal */}
        {loading ? (
          <div
            style={{
              backgroundColor: "#fff",
              borderRadius: "10px",
              boxShadow: "0 2px 10px rgba(44,85,69,0.08)",
              padding: "60px 0",
              display: "flex",
              justifyContent: "center",
            }}
          >
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div
            style={{
              backgroundColor: "#fff",
              borderRadius: "10px",
              boxShadow: "0 2px 10px rgba(44,85,69,0.08)",
              padding: "48px 0",
              textAlign: "center",
            }}
          >
            <p
              style={{
                fontFamily: "'Lato', sans-serif",
                color: "#d4183d",
                fontSize: "14px",
              }}
            >
              {error}
            </p>
            <button
              onClick={cargarCategorias}
              style={{
                marginTop: "12px",
                fontFamily: "'Lato', sans-serif",
                fontSize: "13px",
                color: "#2C5545",
                backgroundColor: "rgba(44,85,69,0.08)",
                border: "none",
                borderRadius: "6px",
                padding: "6px 16px",
                cursor: "pointer",
              }}
            >
              Reintentar
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div
            style={{
              backgroundColor: "#fff",
              borderRadius: "10px",
              boxShadow: "0 2px 10px rgba(44,85,69,0.08)",
              padding: "60px 0",
              display: "flex",
              justifyContent: "center",
            }}
          >
            <EmptyState
              icon={<Tag size={28} style={{ color: "rgba(44,85,69,0.35)" }} />}
              title={search ? "Sin resultados" : "Sin categorías registradas"}
              description={
                search
                  ? `No se encontraron categorías con "${search}".`
                  : "Crea tu primera categoría para organizar el menú."
              }
            />
          </div>
        ) : (
          <DataTable columns={columns} data={filtered} />
        )}
 
        {/* Pie de tabla */}
        {filtered.length > 0 && !loading && (
          <p
            style={{
              fontFamily: "'Lato', sans-serif",
              color: "rgba(44,85,69,0.45)",
              fontSize: "13px",
              marginTop: "14px",
              paddingLeft: "4px",
            }}
          >
            Mostrando {filtered.length} de {categorias.length} categorías
            {search && ` para "${search}"`}
          </p>
        )}
      </div>
 
      {/* ── Modales ─────────────────────────────────────────────────────────── */}
 
      {/* Crear categoría */}
      {showCreateModal && (
        <CategoryModal
          onClose={() => setShowCreateModal(false)}
          onSave={handleCreated}
          
        />
      )}
 
      {/* Confirmar desactivación */}
      {confirmTarget && (
        <ConfirmDeactivateModal
          categoryName={confirmTarget.nombre}
          onClose={() => {
            setConfirmTarget(null);
            setDeactivateError(null);
          }}
          onConfirm={handleConfirmDeactivate}
          loading={deactivating}
          errorMessage={deactivateError}
        />
      )}
    </div>
  );
}
 
function ConfirmDeactivateModal({ categoryName, onClose, onConfirm, loading, errorMessage }) {
  const hasProductError =
    errorMessage && errorMessage.toLowerCase().includes("productos disponibles");
 
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
          padding: "28px 28px 24px",
        }}
      >
        <div className="flex flex-col items-center text-center gap-4">
          <div
            style={{
              backgroundColor: hasProductError
                ? "rgba(212,24,61,0.1)"
                : "rgba(201,168,76,0.15)",
              borderRadius: "50%",
              width: 56,
              height: 56,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Tag size={24} style={{ color: hasProductError ? "#d4183d" : "#C9A84C" }} />
          </div>
 
          <div>
            <h3
              style={{
                fontFamily: "'Playfair Display', serif",
                color: "#2C5545",
                fontSize: "18px",
                fontWeight: 600,
                marginBottom: "8px",
              }}
            >
              {hasProductError ? "No se puede desactivar" : "¿Desactivar categoría?"}
            </h3>
            <p
              style={{
                fontFamily: "'Lato', sans-serif",
                color: "rgba(44,85,69,0.7)",
                fontSize: "14px",
                lineHeight: 1.5,
              }}
            >
              {hasProductError ? (
                <>
                  La categoría{" "}
                  <strong style={{ color: "#2C5545" }}>"{categoryName}"</strong> tiene
                  productos disponibles asociados. Debes desactivarlos o reasignarlos
                  primero.
                </>
              ) : errorMessage ? (
                <span style={{ color: "#d4183d" }}>{errorMessage}</span>
              ) : (
                <>
                  La categoría{" "}
                  <strong style={{ color: "#2C5545" }}>"{categoryName}"</strong> quedará
                  inactiva y no aparecerá en la carta. ¿Estás seguro?
                </>
              )}
            </p>
          </div>
 
          {hasProductError || (errorMessage && !hasProductError) ? (
            <button
              onClick={onClose}
              style={{
                fontFamily: "'Lato', sans-serif",
                backgroundColor: "#2C5545",
                color: "#F8F4EE",
                borderRadius: "8px",
                padding: "10px 24px",
                fontSize: "14px",
                border: "none",
                cursor: "pointer",
                width: "100%",
              }}
            >
              Entendido
            </button>
          ) : (
            <div className="flex gap-3 w-full">
              <button
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
                  flex: 1,
                  opacity: loading ? 0.5 : 1,
                }}
              >
                Cancelar
              </button>
              <button
                onClick={onConfirm}
                disabled={loading}
                style={{
                  fontFamily: "'Lato', sans-serif",
                  backgroundColor: loading ? "rgba(212,24,61,0.5)" : "#d4183d",
                  color: "#fff",
                  borderRadius: "8px",
                  padding: "9px 20px",
                  fontSize: "14px",
                  border: "none",
                  cursor: loading ? "not-allowed" : "pointer",
                  flex: 1,
                }}
              >
                {loading ? "Desactivando…" : "Desactivar"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
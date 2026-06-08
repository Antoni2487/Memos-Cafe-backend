import { Tag, Plus } from "lucide-react";
import { useCategorias } from "../../hooks/useCategorias";
import {
  PageHeader,
  DataTable,
  StatusBadge,
  LoadingSpinner,
  EmptyState,
  StatCard,
  SearchBar,
  ConfirmDialog,
} from "../../components/common";
import { CategoryModal } from "../../components/categorias/Categoriamodal";

export default function CategoriasPage() {
  const {
    categorias, filtered, loading, error,
    search, setSearch,
    showModal, setShowModal,
    confirmTarget, deactivating, deactivateError,
    cargar, handleCreated, pedirConfirmacion,
    confirmarDesactivar, cancelarConfirm,
  } = useCategorias();

  const columnas = [
    {
      key: "nombre",
      label: "Nombre",
      render: (cat) => (
        <div className="flex items-center gap-3">
          <div style={{
            backgroundColor: cat.activo ? "rgba(201,168,76,0.15)" : "rgba(0,0,0,0.06)",
            borderRadius: "7px", width: 34, height: 34,
            display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
          }}>
            <Tag size={15} style={{ color: cat.activo ? "#C9A84C" : "rgba(44,85,69,0.3)" }} />
          </div>
          <span style={{
            fontFamily: "'Lato', sans-serif",
            color: cat.activo ? "#2C5545" : "rgba(44,85,69,0.4)",
            fontSize: 15, fontWeight: 500,
            textDecoration: cat.activo ? "none" : "line-through",
          }}>
            {cat.nombre}
          </span>
        </div>
      ),
    },
    {
      key: "activo",
      label: "Estado",
      render: (cat) => <StatusBadge estado={cat.activo ? "activo" : "inactivo"} />,
    },
    {
      key: "acciones",
      label: "Acciones",
      render: (cat) =>
        cat.activo ? (
          <button
            onClick={() => pedirConfirmacion(cat)}
            style={{
              fontFamily: "'Lato', sans-serif", fontSize: 13,
              color: "#d4183d", backgroundColor: "rgba(212,24,61,0.07)",
              border: "none", borderRadius: 6, padding: "6px 14px",
              cursor: "pointer", fontWeight: 500, transition: "background-color 0.15s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(212,24,61,0.14)")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "rgba(212,24,61,0.07)")}
          >
            Desactivar
          </button>
        ) : (
          <span style={{
            fontFamily: "'Lato', sans-serif", fontSize: 12,
            color: "rgba(44,85,69,0.35)", fontStyle: "italic",
          }}>
            Inactiva
          </span>
        ),
    },
  ];

  const activeCount   = categorias.filter((c) => c.activo).length;
  const inactiveCount = categorias.filter((c) => !c.activo).length;

  // Mensaje del confirm dialog
  const hasProductError = deactivateError?.toLowerCase().includes("productos disponibles");
  const confirmDesc = hasProductError
    ? `"${confirmTarget?.nombre}" tiene productos disponibles asociados. Desactívalos primero.`
    : deactivateError
    ? deactivateError
    : `"${confirmTarget?.nombre}" quedará inactiva y no aparecerá en la carta. ¿Estás seguro?`;

  return (
    <>
      <PageHeader
        titulo="Categorías"
        descripcion="Organiza el menú agrupando los productos por categoría"
        accion={
          <button
            onClick={() => setShowModal(true)}
            style={{
              fontFamily: "'Lato', sans-serif", backgroundColor: "#2C5545",
              color: "#F8F4EE", borderRadius: 8, padding: "9px 20px",
              fontSize: 14, fontWeight: 600, border: "none", cursor: "pointer",
              display: "flex", alignItems: "center", gap: 8, whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#234438")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#2C5545")}
          >
            <Plus size={16} />
            Nueva categoría
          </button>
        }
      />

      {/* Stats */}
      <div className="flex gap-4 mb-6">
        <StatCard titulo="Total categorías" valor={categorias.length} />
        <StatCard titulo="Activas"           valor={activeCount} />
        <StatCard titulo="Inactivas"         valor={inactiveCount} />
      </div>

      {/* Búsqueda */}
      <div style={{
        backgroundColor: "#fff", borderRadius: 10,
        boxShadow: "0 2px 10px rgba(44,85,69,0.08)",
        padding: "14px 18px", marginBottom: 20,
      }}>
        <SearchBar
          placeholder="Buscar por nombre…"
          onBuscar={setSearch}
        />
      </div>

      {/* Tabla */}
      <DataTable
        columnas={columnas}
        datos={filtered}
        cargando={loading}
        textoVacio={
          error
            ? `Error: ${error}`
            : search
            ? `Sin resultados para "${search}"`
            : "Sin categorías registradas"
        }
      />

      {/* Pie */}
      {filtered.length > 0 && !loading && (
        <p style={{
          fontFamily: "'Lato', sans-serif", color: "rgba(44,85,69,0.45)",
          fontSize: 13, marginTop: 14, paddingLeft: 4,
        }}>
          Mostrando {filtered.length} de {categorias.length} categorías
          {search && ` para "${search}"`}
        </p>
      )}

      {/* Modal crear */}
      {showModal && (
        <CategoryModal
          onClose={() => setShowModal(false)}
          onSave={handleCreated}
        />
      )}

      {/* Confirm desactivar */}
      <ConfirmDialog
        abierto={!!confirmTarget}
        titulo={hasProductError ? "No se puede desactivar" : "¿Desactivar categoría?"}
        descripcion={confirmDesc}
        textoOk={hasProductError || deactivateError ? undefined : "Desactivar"}
        textoCancelar={hasProductError || deactivateError ? "Entendido" : "Cancelar"}
        variante="danger"
        cargando={deactivating}
        onConfirmar={hasProductError || deactivateError ? cancelarConfirm : confirmarDesactivar}
        onCancelar={cancelarConfirm}
      />
    </>
  );
}

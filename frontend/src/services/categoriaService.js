const BASE_URL = "/api/productos/categorias";
 
function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}
 
const categoriaService = {
  async listar() {
    const res = await fetch(`${BASE_URL}/`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Error al cargar categorías");
    return res.json(); 
  },

  async crear(nombre) {
    const res = await fetch(`${BASE_URL}/crear/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ nombre }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error al crear la categoría");
    return data;
  },
 
  async desactivar(id) {
    const res = await fetch(`${BASE_URL}/${id}/desactivar/`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error al desactivar");
    return data;
  },
};
 
export default categoriaService;
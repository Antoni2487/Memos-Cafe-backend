import api from "./api";

const rolesService = {
  getAll:  ()         => api.get("/roles/permisos/"),
  update:  (pk, data) => api.patch(`/roles/permisos/${pk}/`, data),
};

export default rolesService;

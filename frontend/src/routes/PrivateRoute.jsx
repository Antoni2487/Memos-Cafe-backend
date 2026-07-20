import { Navigate, Outlet } from "react-router-dom";
import authService from "../services/authService";

export default function PrivateRoute({ roles = [] }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (roles.length > 0) {
    const userRoles = JSON.parse(localStorage.getItem("user_roles") || "[]");
    const tieneAcceso = roles.some((rol) => userRoles.includes(rol));
    if (!tieneAcceso) {
      return <Navigate to="/" replace />;
    }
  }

  return <Outlet />;
}
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import PrivateRoute from "./PrivateRoute";
import { ROLES } from "../utils/constants";

// Pages
import LoginPage from "../pages/auth/LoginPage";
import DashboardPage from "../pages/dashboard/DashboardPage";
import MesasPage from "../pages/mesas/MesasPage";
import OrdenesPage from "../pages/ordenes/OrdenesPage";
import ComandaPage from "../pages/ordenes/ComandaPage";
import ProductosPage from "../pages/productos/ProductosPage";
import CajaPage from "../pages/caja/CajaPage";
import ReportesPage from "../pages/reportes/ReportesPage";
import InsumosPage from "../pages/insumos/InsumosPage";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Pública */}
        <Route path="/login" element={<LoginPage />} />

        {/* Todos los roles autenticados */}
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/mesas" element={<MesasPage />} />
          <Route path="/ordenes" element={<OrdenesPage />} />
          <Route path="/comanda" element={<ComandaPage />} />
        </Route>

        {/* Solo admin y cajero */}
        <Route element={<PrivateRoute roles={[ROLES.ADMIN, ROLES.CAJERO]} />}>
          <Route path="/caja" element={<CajaPage />} />
        </Route>

        {/* Solo admin */}
        <Route element={<PrivateRoute roles={[ROLES.ADMIN]} />}>
          <Route path="/productos" element={<ProductosPage />} />
          <Route path="/reportes" element={<ReportesPage />} />
          <Route path="/insumos" element={<InsumosPage />} />
        </Route>

        {/* Redirige raíz al dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
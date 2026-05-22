import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../store/useAuthStore";

export function ProtectedRoute() {
  const isAuth = useAuthStore((state) => state.isAuthentication);

  if (!isAuth) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

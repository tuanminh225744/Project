import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/useAuthStore";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuth = useAuthStore((state) => state.isAuthentication);

  if (!isAuth) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

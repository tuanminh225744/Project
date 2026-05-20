import { Navigate } from "react-router-dom";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuth = Boolean(localStorage.getItem("accessToken"));

  if (!isAuth) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

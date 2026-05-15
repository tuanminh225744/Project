import { Navigate } from "react-router-dom";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuth = false; // giả lập login

  if (!isAuth) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

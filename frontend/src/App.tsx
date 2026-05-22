import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
// import { Project } from "./pages/project";
// import { ProjectDetail } from "./pages/project_detail";
import { ProtectedRoute } from "./hooks/protected_router";

const Project = lazy(() => import("./pages/project"));
const ProjectDetail = lazy(() => import("./pages/project_detail"));
const Login = lazy(() => import("./pages/login"));
const Register = lazy(() => import("./pages/register"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Login />} />
        {/* <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        /> */}
        <Route element={<ProtectedRoute />}>
          <Route path="/project" element={<Project />} />
          <Route path="/project/:projectId" element={<ProjectDetail />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;

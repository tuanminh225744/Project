import Dashboard from "./pages/dashboard";
import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
// import { Project } from "./pages/project";
// import { ProjectDetail } from "./pages/project_detail";
import { ProtectedRoute } from "./hooks/protected_router";

const Project = lazy(() => import("./pages/project"));
const ProjectDetail = lazy(() => import("./pages/project_detail"));
const User = lazy(() => import("./pages/user"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/project" element={<Project />}>
          <Route path="/project/:projectId" element={<ProjectDetail />} />
        </Route>
        <Route path="/user" element={<User />} />
      </Routes>
    </Suspense>
  );
}

export default App;

import axiosInstance from "../api";
import { type ProjectMember } from "./project_member_service";

export interface Project {
  id: number;
  name: string;
  description?: string | null;
  priority: "low" | "medium" | "high";
  due_date?: string | null;
  owner_id: number;
  created_at: string;
  updated_at?: string | null;
  members: ProjectMember[];
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  priority: "low" | "medium" | "high";
  due_date: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string;
  priority?: "low" | "medium" | "high";
  due_date?: string;
  status?: "todo" | "in_progress" | "done";
}

export const getProjectsApi = async () => {
  return axiosInstance.get<Project[], Project[]>("/projects/");
};

export const createProjectApi = async (payload: CreateProjectPayload) => {
  return axiosInstance.post<Project, Project>("/projects/", payload);
};

export const getProjectByIdApi = async (projectId: number) => {
  return axiosInstance.get<Project, Project>(`/projects/${projectId}`);
};

export const updateProjectApi = async (
  projectId: number,
  payload: UpdateProjectPayload,
) => {
  return axiosInstance.put<Project, Project>(`/projects/${projectId}`, payload);
};

export const deleteProjectApi = async (projectId: number) => {
  return axiosInstance.delete<Project, Project>(`/projects/${projectId}`);
};

import axiosInstance from "../api";

export interface Project {
  id: number;
  name: string;
  description?: string | null;
  priority: "low" | "medium" | "high";
  due_date?: string | null;
  owner_id: number;
  created_at: string;
  updated_at?: string | null;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  priority: "low" | "medium" | "high";
  due_date: string;
}

export const getProjectsApi = async () => {
  return axiosInstance.get<Project[], Project[]>("/projects/");
};

export const createProjectApi = async (payload: CreateProjectPayload) => {
  return axiosInstance.post<Project, Project>("/projects/", payload);
};

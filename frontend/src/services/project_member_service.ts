import axiosInstance from "../api";
import { type User } from "./user_service";
import { type Project } from "./project_service";

export interface ProjectMember {
  id: number;
  project_id: Number;
  user_id: Number;
  role: "member" | "owner";
  user: User;
  project: Project;
}

export const getProjectMembersApi = async (projectId: number) => {
  return axiosInstance.get<ProjectMember[], ProjectMember[]>(
    `/projects/${projectId}/members`,
  );
};

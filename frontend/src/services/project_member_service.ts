import axiosInstance from "../api";
import { type User } from "./user_service";

export interface ProjectMember {
  id: number;
  project_id: Number;
  user_id: Number;
  role: "member" | "owner";
  user: User;
}

export const getProjectMembersApi = async (projectId: number) => {
  return axiosInstance.get<ProjectMember[], ProjectMember[]>(
    `/projects/${projectId}/members`,
  );
};

export const addMemberApi = (projectId: number, userId: number) => {
  return axiosInstance.post(`/projects/${projectId}/members`, {
    user_id: userId,
    project_id: projectId,
  });
};

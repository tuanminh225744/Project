import axiosInstance from "../api";

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string | null;
  avatar_url?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
}

export const getUsersApi = () => {
  return axiosInstance.get<User[], User[]>(`/users`);
};

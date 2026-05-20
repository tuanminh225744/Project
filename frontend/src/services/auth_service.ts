import axiosInstance from "../api";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  message: string;
  user_id: number;
  username: string;
}

export const loginApi = async (payload: LoginPayload) => {
  const formData = new URLSearchParams();
  formData.append("username", payload.username);
  formData.append("password", payload.password);

  return axiosInstance.post<LoginResponse, LoginResponse>("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
};

export const registerApi = async (payload: RegisterPayload) => {
  return axiosInstance.post<RegisterResponse, RegisterResponse>("/auth/register", payload);
};

import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import {
  loginApi,
  registerApi,
  type LoginPayload,
  type RegisterPayload,
} from "../services/auth_service";
import { type User } from "../services/user_service";

const getStoredAccessToken = () =>
  typeof window === "undefined" ? null : localStorage.getItem("accessToken");

const getStoredRefreshToken = () =>
  typeof window === "undefined" ? null : localStorage.getItem("refreshToken");

interface AuthState {
  user: User | null;
  access_token: string | null;
  refresh_token: string | null;
  isAuthentication: boolean;
  isLoading: boolean;
  error: string | null;

  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  updateProfile: (profileData: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        access_token: getStoredAccessToken(),
        refresh_token: getStoredRefreshToken(),
        isAuthentication: Boolean(getStoredAccessToken()),
        isLoading: false,
        error: null,

        login: async (payload) => {
          set({ isLoading: true, error: null });

          try {
            const response = await loginApi(payload);

            localStorage.setItem("accessToken", response.access_token);
            localStorage.setItem("refreshToken", response.refresh_token);

            set({
              access_token: response.access_token,
              refresh_token: response.refresh_token,
              user: response.user,
              isAuthentication: true,
              isLoading: false,
              error: null,
            });
          } catch (error) {
            set({
              isLoading: false,
              error: "Username hoặc password không đúng.",
            });
            throw error;
          }
        },

        register: async (payload) => {
          set({ isLoading: true, error: null });

          try {
            await registerApi(payload);
            set({ isLoading: false, error: null });
          } catch (error) {
            set({
              isLoading: false,
              error:
                "Không thể đăng ký tài khoản. Vui lòng kiểm tra lại thông tin.",
            });
            throw error;
          }
        },

        logout: () => {
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");

          set({
            user: null,
            access_token: null,
            refresh_token: null,
            isAuthentication: false,
            error: null,
          });
        },

        clearError: () => set({ error: null }),

        updateProfile: (profileData) =>
          set((state) => ({
            user: state.user ? { ...state.user, ...profileData } : null,
          })),
      }),
      {
        name: "auth-storage",
        partialize: (state) => ({
          user: state.user,
          access_token: state.access_token,
          refresh_token: state.refresh_token,
          isAuthentication: state.isAuthentication,
        }),
      },
    ),
    { name: "AuthStore" },
  ),
);

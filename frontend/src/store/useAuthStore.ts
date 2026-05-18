import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

export interface User {
  userId: number | string;
  email: string;
  username: string;
  full_name: string;
  avatar_url: string | null;
}

interface AuthState {
  user: User | null;
  access_token: string | null;
  isAuthentication: boolean;

  login: (user: User, token: string) => void;
  logout: () => void;
  updateProfile: (profileData: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        access_token: null,
        isAuthentication: false,

        login: (user, token) =>
          set({
            user: user,
            access_token: token,
            isAuthentication: true,
          }),

        logout: () =>
          set({
            user: null,
            access_token: null,
            isAuthentication: false,
          }),

        updateProfile: (profileData) =>
          set((state) => ({
            user: state.user ? { ...state.user, ...profileData } : null,
          })),
      }),
      {
        name: "auth-storage",
      },
    ),
    { name: "AuthStore" },
  ),
);

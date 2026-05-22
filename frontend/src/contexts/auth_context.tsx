import { createContext, useContext, useState } from "react";

const AuthContext = createContext<any>(null);

type User = {
  name: string;
};

export function AuthProvider({ children }: any) {
  const [user, setUser] = useState<User | null>();

  const login = () => {
    setUser({
      name: "John",
    });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
// file này chỉ là file học, không phải file dự án

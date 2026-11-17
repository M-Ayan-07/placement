"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { api, setAccessToken } from "@/lib/api";

export interface User {
  id: string;
  email: string;
  role: string;
  profile?: {
    full_name: string;
    college?: string;
    branch?: string;
    graduation_year?: number;
    cgpa?: number;
    skills: string[];
    bio?: string;
  };
  goals?: {
    target_roles: string[];
    target_companies: string[];
    target_ctc_lpa?: number;
    preferred_locations: string[];
  };
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => Promise<void>;
  updateUser: (userData: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Attempt silent session recovery on boot via /auth/refresh cookie
    async function initAuth() {
      try {
        const data = await api.post<{ access_token: string }>("/auth/refresh");
        setAccessToken(data.access_token);
        const profile = await api.get<User>("/profile/me");
        setUser(profile);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }
    initAuth();
  }, []);

  const login = (token: string, userData: User) => {
    setAccessToken(token);
    setUser(userData);
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // Ignore network errors on logout
    } finally {
      setAccessToken(null);
      setUser(null);
      window.location.href = "/login";
    }
  };

  const updateUser = (userData: User) => {
    setUser(userData);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}


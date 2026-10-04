import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, TOKEN_KEY } from "../api/client";
import type { Profile } from "../api/types";

interface AuthState {
  profile: Profile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<Profile>;
  register: (name: string, email: string, password: string) => Promise<Profile>;
  logout: () => void;
  refresh: () => Promise<Profile | null>;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!localStorage.getItem(TOKEN_KEY)) {
      setProfile(null);
      return null;
    }
    try {
      const { data } = await api.get<Profile>("/student/profile");
      setProfile(data);
      return data;
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      setProfile(null);
      return null;
    }
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const afterToken = useCallback(async (token: string) => {
    localStorage.setItem(TOKEN_KEY, token);
    const p = await refresh();
    if (!p) throw new Error("Could not load your profile");
    return p;
  }, [refresh]);

  const value = useMemo<AuthState>(() => ({
    profile, loading, refresh,
    login: async (email, password) => afterToken((await api.post("/auth/login", { email, password })).data.access_token),
    register: async (name, email, password) =>
      afterToken((await api.post("/auth/register", { name, email, password })).data.access_token),
    logout: () => { localStorage.removeItem(TOKEN_KEY); setProfile(null); },
  }), [profile, loading, refresh, afterToken]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth outside AuthProvider");
  return v;
}

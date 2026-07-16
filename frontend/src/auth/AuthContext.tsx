import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { getToken, setToken, setUnauthorizedHandler } from '../api/client';
import { fetchMe, login as apiLogin, register as apiRegister } from '../api/endpoints';
import type { UserResponse } from '../api/types';

interface AuthContextValue {
  user: UserResponse | null;
  /** True while the persisted token is being validated on startup. */
  initializing: boolean;
  isAgent: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const USER_KEY = 'helpdesk.user';

function readStoredUser(): UserResponse | null {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as UserResponse) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(() =>
    getToken() ? readStoredUser() : null,
  );
  const [initializing, setInitializing] = useState<boolean>(() => getToken() !== null);

  const logout = useCallback(() => {
    setToken(null);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    return () => setUnauthorizedHandler(null);
  }, [logout]);

  // Revalidate the persisted session (also refreshes role if an admin changed it).
  useEffect(() => {
    if (!getToken()) return;
    let cancelled = false;
    fetchMe()
      .then((me) => {
        if (cancelled) return;
        setUser(me);
        localStorage.setItem(USER_KEY, JSON.stringify(me));
      })
      .catch(() => {
        // 401 is handled by the unauthorized handler; network errors keep the cached user
      })
      .finally(() => {
        if (!cancelled) setInitializing(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const applyAuth = useCallback((token: string, authedUser: UserResponse) => {
    setToken(token);
    localStorage.setItem(USER_KEY, JSON.stringify(authedUser));
    setUser(authedUser);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await apiLogin(email, password);
      applyAuth(response.token, response.user);
    },
    [applyAuth],
  );

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      const response = await apiRegister(email, password, fullName);
      applyAuth(response.token, response.user);
    },
    [applyAuth],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      initializing,
      isAgent: user?.role === 'AGENT' || user?.role === 'ADMIN',
      isAdmin: user?.role === 'ADMIN',
      login,
      register,
      logout,
    }),
    [user, initializing, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

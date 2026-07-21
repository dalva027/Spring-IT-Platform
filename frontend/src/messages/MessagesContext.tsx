import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { fetchUnreadCount } from '../api/endpoints';
import { useAuth } from '../auth/AuthContext';

interface MessagesContextValue {
  unreadCount: number;
  /** Re-fetch the unread count (call after reading or sending a message). */
  refresh: () => void;
}

const MessagesContext = createContext<MessagesContextValue | null>(null);

const POLL_INTERVAL_MS = 60_000;

export function MessagesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  const refresh = useCallback(() => {
    if (!user) return;
    fetchUnreadCount()
      .then(setUnreadCount)
      .catch(() => {
        // Non-fatal: the badge simply won't update.
      });
  }, [user]);

  useEffect(() => {
    if (!user) {
      setUnreadCount(0);
      return;
    }
    refresh();
    const id = window.setInterval(refresh, POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [user, refresh]);

  const value = useMemo(() => ({ unreadCount, refresh }), [unreadCount, refresh]);

  return <MessagesContext.Provider value={value}>{children}</MessagesContext.Provider>;
}

export function useMessages(): MessagesContextValue {
  const ctx = useContext(MessagesContext);
  if (!ctx) throw new Error('useMessages must be used within MessagesProvider');
  return ctx;
}

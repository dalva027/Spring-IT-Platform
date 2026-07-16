import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { fetchUsers } from '../api/endpoints';
import type { UserResponse } from '../api/types';
import { useAuth } from './AuthContext';

interface UserDirectoryValue {
  users: UserResponse[];
  /** Agents and admins for the assignee picker. */
  agents: UserResponse[];
  displayName: (userId: number | null | undefined) => string;
  reload: () => void;
}

const UserDirectoryContext = createContext<UserDirectoryValue | null>(null);

/**
 * Only agents/admins may call GET /api/users, so for requesters the directory
 * stays empty and ids render as "User #<id>" (or "You" for their own id).
 */
export function UserDirectoryProvider({ children }: { children: ReactNode }) {
  const { user, isAgent } = useAuth();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [reloadCounter, setReloadCounter] = useState(0);

  useEffect(() => {
    if (!isAgent) {
      setUsers([]);
      return;
    }
    let cancelled = false;
    fetchUsers()
      .then((list) => {
        if (!cancelled) setUsers(list);
      })
      .catch(() => {
        // Non-fatal: ids simply render without names
      });
    return () => {
      cancelled = true;
    };
  }, [isAgent, reloadCounter]);

  const value = useMemo<UserDirectoryValue>(() => {
    const byId = new Map(users.map((u) => [u.id, u]));
    return {
      users,
      agents: users.filter((u) => u.role === 'AGENT' || u.role === 'ADMIN'),
      displayName: (userId) => {
        if (userId === null || userId === undefined) return 'Unassigned';
        if (user && userId === user.id) return `${user.fullName} (you)`;
        const found = byId.get(userId);
        return found ? found.fullName : `User #${userId}`;
      },
      reload: () => setReloadCounter((n) => n + 1),
    };
  }, [users, user]);

  return <UserDirectoryContext.Provider value={value}>{children}</UserDirectoryContext.Provider>;
}

export function useUserDirectory(): UserDirectoryValue {
  const ctx = useContext(UserDirectoryContext);
  if (!ctx) throw new Error('useUserDirectory must be used within UserDirectoryProvider');
  return ctx;
}

import { useState } from 'react';
import { updateUserRole } from '../api/endpoints';
import type { Role } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { useUserDirectory } from '../auth/UserDirectoryContext';
import { RoleBadge, formatDateTime } from '../components/badges';
import { EmptyState, ErrorMessage } from '../components/feedback';

const ROLES: Role[] = ['REQUESTER', 'AGENT', 'ADMIN'];

export function UsersPage() {
  const { user: currentUser, isAdmin } = useAuth();
  const { users, reload } = useUserDirectory();
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);

  async function handleRoleChange(userId: number, role: Role) {
    setError(null);
    setSavingId(userId);
    try {
      await updateUserRole(userId, role);
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update role');
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div>
      <h1>Users</h1>
      {error && <ErrorMessage message={error} />}
      {users.length === 0 ? (
        <EmptyState message="No users loaded." />
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Joined</th>
                {isAdmin && <th>Change role</th>}
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>
                    {user.fullName}
                    {currentUser?.id === user.id && <span className="detail-sub"> (you)</span>}
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <RoleBadge role={user.role} />
                  </td>
                  <td>{formatDateTime(user.createdAt)}</td>
                  {isAdmin && (
                    <td>
                      <select
                        value={user.role}
                        disabled={savingId === user.id || currentUser?.id === user.id}
                        onChange={(e) => handleRoleChange(user.id, e.target.value as Role)}
                      >
                        {ROLES.map((role) => (
                          <option key={role} value={role}>
                            {role}
                          </option>
                        ))}
                      </select>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

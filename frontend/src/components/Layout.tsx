import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { RoleBadge } from './badges';
import { Sidebar } from './Sidebar';
import { ThemeToggle } from './ThemeToggle';

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(true);

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="app-shell">
      <Sidebar collapsed={collapsed} onCollapseChange={setCollapsed} />
      <div className="app-main">
        <header className="topbar">
          <div className="topbar-brand">
            <span className="brand-mark" aria-hidden="true" />
            <span className="brand-name">floIT</span>
          </div>
          <div className="topbar-user">
            <ThemeToggle />
            {user && (
              <>
                <span className="user-name">{user.fullName}</span>
                <RoleBadge role={user.role} />
                <button type="button" className="btn-ghost" onClick={handleLogout}>
                  Sign out
                </button>
              </>
            )}
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

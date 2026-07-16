import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { RoleBadge } from './badges';
import { ThemeToggle } from './ThemeToggle';

export function Layout() {
  const { user, isAgent, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">Helpdesk</span>
        </div>
        <nav className="topbar-nav">
          <NavLink to="/tickets" end>
            Tickets
          </NavLink>
          <NavLink to="/tickets/new">New ticket</NavLink>
          {isAgent && <NavLink to="/reports">Reports</NavLink>}
          {isAgent && <NavLink to="/users">Users</NavLink>}
        </nav>
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
  );
}

import type { ReactElement } from 'react';
import { BrowserRouter, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { ThemeProvider } from './theme/ThemeContext';
import { UserDirectoryProvider } from './auth/UserDirectoryContext';
import { Layout } from './components/Layout';
import { Spinner } from './components/feedback';
import { LoginPage } from './pages/LoginPage';
import { NewTicketPage } from './pages/NewTicketPage';
import { RegisterPage } from './pages/RegisterPage';
import { ReportsPage } from './pages/ReportsPage';
import { TicketDetailPage } from './pages/TicketDetailPage';
import { TicketsPage } from './pages/TicketsPage';
import { UsersPage } from './pages/UsersPage';

function RequireAuth() {
  const { user, initializing } = useAuth();
  const location = useLocation();
  if (initializing && !user) return <Spinner label="Loading…" />;
  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname + location.search }} replace />;
  }
  return <Outlet />;
}

function RequireAgent() {
  const { isAgent } = useAuth();
  if (!isAgent) return <Navigate to="/tickets" replace />;
  return <Outlet />;
}

function RedirectIfAuthed({ children }: { children: ReactElement }) {
  const { user } = useAuth();
  if (user) return <Navigate to="/tickets" replace />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
        <Routes>
          <Route
            path="/login"
            element={
              <RedirectIfAuthed>
                <LoginPage />
              </RedirectIfAuthed>
            }
          />
          <Route
            path="/register"
            element={
              <RedirectIfAuthed>
                <RegisterPage />
              </RedirectIfAuthed>
            }
          />
          <Route element={<RequireAuth />}>
            <Route
              element={
                <UserDirectoryProvider>
                  <Layout />
                </UserDirectoryProvider>
              }
            >
              <Route path="/" element={<Navigate to="/tickets" replace />} />
              <Route path="/tickets" element={<TicketsPage />} />
              <Route path="/tickets/new" element={<NewTicketPage />} />
              <Route path="/tickets/:id" element={<TicketDetailPage />} />
              <Route element={<RequireAgent />}>
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/users" element={<UsersPage />} />
              </Route>
              <Route path="*" element={<Navigate to="/tickets" replace />} />
            </Route>
          </Route>
        </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

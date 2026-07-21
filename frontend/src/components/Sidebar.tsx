import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useMessages } from '../messages/MessagesContext';

interface SidebarItem {
  label: string;
  /** Destination, including any query string (e.g. /tickets?mine=1). */
  to: string;
  agentOnly?: boolean;
  /** Show the unread-messages badge on this item. */
  showUnread?: boolean;
  /** Query-aware active check — NavLink can't see the query string, so we match ourselves. */
  isActive: (pathname: string, search: URLSearchParams) => boolean;
  icon: ReactNode;
}

/* Inline stroke icons in the lucide style, matching the project's SVG convention (see ThemeToggle). */
function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={20}
      height={20}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const isTicketDetail = (pathname: string) => /^\/tickets\/\d+$/.test(pathname);

const sidebarItems: SidebarItem[] = [
  {
    label: 'Inbox',
    to: '/inbox',
    showUnread: true,
    // Internal messaging inbox.
    isActive: (pathname) => pathname === '/inbox',
    icon: (
      <Icon>
        <path d="M22 12h-6l-2 3h-4l-2-3H2" />
        <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11Z" />
      </Icon>
    ),
  },
  {
    label: 'Tickets',
    to: '/tickets',
    // "All tickets" — the /tickets list (incl. the Unassigned filter) or a ticket detail, but not the mine view.
    isActive: (pathname, search) =>
      (pathname === '/tickets' && search.get('mine') !== '1') || isTicketDetail(pathname),
    icon: (
      <Icon>
        <path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z" />
        <path d="M13 5v2M13 17v2M13 11v2" />
      </Icon>
    ),
  },
  {
    label: 'My Tickets',
    to: '/tickets?mine=1',
    agentOnly: true,
    // Tickets assigned to the current user — the /tickets?mine=1 view.
    isActive: (pathname, search) => pathname === '/tickets' && search.get('mine') === '1',
    icon: (
      <Icon>
        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
        <path d="M9 2h6a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Z" />
        <path d="m9 14 2 2 4-4" />
      </Icon>
    ),
  },
  {
    label: 'New ticket',
    to: '/tickets/new',
    isActive: (pathname) => pathname === '/tickets/new',
    icon: (
      <Icon>
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2Z" />
        <path d="M14 2v6h6M12 18v-6M9 15h6" />
      </Icon>
    ),
  },
  {
    label: 'Get help',
    to: '/assist',
    isActive: (pathname) => pathname === '/assist',
    icon: (
      <Icon>
        <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />
      </Icon>
    ),
  },
  {
    label: 'Reports',
    to: '/reports',
    agentOnly: true,
    isActive: (pathname) => pathname === '/reports',
    icon: (
      <Icon>
        <path d="M3 3v18h18M18 17V9M13 17V5M8 17v-3" />
      </Icon>
    ),
  },
  {
    label: 'Users',
    to: '/users',
    agentOnly: true,
    isActive: (pathname) => pathname === '/users',
    icon: (
      <Icon>
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      </Icon>
    ),
  },
];

interface SidebarProps {
  collapsed: boolean;
  onCollapseChange: (collapsed: boolean) => void;
}

export function Sidebar({ collapsed, onCollapseChange }: SidebarProps) {
  const { isAgent } = useAuth();
  const { unreadCount } = useMessages();
  const location = useLocation();
  const search = new URLSearchParams(location.search);
  const items = sidebarItems.filter((item) => !item.agentOnly || isAgent);

  return (
    <aside
      className={`sidebar ${collapsed ? 'sidebar--collapsed' : 'sidebar--expanded'}`}
      onMouseEnter={() => onCollapseChange(false)}
      onMouseLeave={() => onCollapseChange(true)}
    >
      <button
        type="button"
        className="sidebar__toggle"
        onClick={() => onCollapseChange(!collapsed)}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          {collapsed ? <path d="m9 18 6-6-6-6" /> : <path d="m15 18-6-6 6-6" />}
        </svg>
      </button>

      <nav className="sidebar__nav">
        {items.map((item) => {
          const active = item.isActive(location.pathname, search);
          const badge = item.showUnread && unreadCount > 0 ? unreadCount : null;
          return (
            <Link
              key={item.label}
              to={item.to}
              className={`sidebar__item ${active ? 'sidebar__item--active' : ''}`}
              title={badge ? `${item.label} (${badge} unread)` : item.label}
            >
              <span className="sidebar__icon">
                {item.icon}
                {badge !== null && <span className="sidebar__dot" aria-hidden="true" />}
              </span>
              <span className="sidebar__label">{item.label}</span>
              {badge !== null && <span className="sidebar__badge">{badge > 99 ? '99+' : badge}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

import React from 'react';
import type { ChatSession } from '../types/chat';
import { Plus, MessageSquare, Trash2, PanelLeftClose, PanelLeftOpen } from 'lucide-react';

interface SidebarProps {
  sessions: ChatSession[];
  activeThreadId: string | null;
  isOpen: boolean;
  collapsed: boolean;
  onToggle: () => void;
  onToggleCollapse: () => void;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
}

/**
 * Persistent sidebar with session history, brand header, and API health indicator.
 * Supports a collapsed state (icon-only strip) toggled via the collapse button.
 */
export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeThreadId,
  isOpen,
  collapsed,
  onToggle,
  onToggleCollapse,
  onSelectSession,
  onNewSession,
  onDeleteSession
}) => {
  return (
    <>
      {/* Mobile backdrop overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onToggle} />}

      <aside className={`sidebar ${isOpen ? 'open' : ''} ${collapsed ? 'collapsed' : ''}`}>
        {/* Brand header */}
        <div className="sidebar-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, overflow: 'hidden' }}>
            {/* Toggle collapse button (the sidebar icon) */}
            <button
              className="icon-btn"
              onClick={onToggleCollapse}
              title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              style={{ flexShrink: 0 }}
            >
              {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
            </button>

            {/* Brand text — hidden when collapsed via CSS */}
            <span className="sidebar-brand-text" style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, fontSize: 14, whiteSpace: 'nowrap' }}>
              Greenway AI
            </span>
          </div>

          {/* New chat button — hidden when collapsed via CSS */}
          <div className="sidebar-header-actions">
            <button className="icon-btn" onClick={onNewSession} title="New Chat">
              <Plus size={16} />
            </button>
          </div>
        </div>

        {/* Session list */}
        <div className="sidebar-sessions">
          <div className="sidebar-section-label" style={{ padding: '4px 10px 8px', fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-dim)' }}>
            Conversations
          </div>

          {sessions.length === 0 ? (
            !collapsed && (
              <div style={{ textAlign: 'center', padding: '32px 0', fontSize: 12, color: 'var(--text-dim)' }}>
                No conversations yet
              </div>
            )
          ) : (
            sessions.map(session => (
              <div
                key={session.id}
                className={`session-item ${session.id === activeThreadId ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
                title={collapsed ? session.title : undefined}
              >
                <MessageSquare
                  size={14}
                  style={{ flexShrink: 0, color: session.id === activeThreadId ? 'var(--accent)' : 'var(--text-dim)' }}
                />
                {/* Session title label — hidden when collapsed via CSS */}
                <span className="session-label" style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', transition: 'opacity 0.2s' }}>
                  {session.title}
                </span>
                <button
                  className="delete-btn icon-btn"
                  onClick={e => { e.stopPropagation(); onDeleteSession(session.id); }}
                  title="Delete"
                  style={{ padding: 4 }}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>
    </>
  );
};

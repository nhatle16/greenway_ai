import { useState, useRef, useEffect } from 'react';
import { useChatStream } from './hooks/useChatStream';
import { Sidebar } from './components/Sidebar';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { PanelLeftOpen, Sparkles } from 'lucide-react';

/**
 * Root application shell with a toggleable sidebar and centered chat content.
 */
export function App() {
  const {
    sessions,
    activeThreadId,
    activeSession,
    isStreaming,
    setActiveThreadId,
    createNewSession,
    deleteSession,
    sendMessage,
    stopStreaming
  } = useChatStream();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  /* Auto-scroll to latest message */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession?.messages, isStreaming]);

  const hasMessages = activeSession && activeSession.messages.length > 0;

  return (
    <div className="app-shell">
      {/* ── Sidebar ── */}
      <Sidebar
        sessions={sessions}
        activeThreadId={activeThreadId}
        isOpen={sidebarOpen}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarOpen(false)}
        onToggleCollapse={() => setSidebarCollapsed(prev => !prev)}
        onSelectSession={id => { setActiveThreadId(id); setSidebarOpen(false); }}
        onNewSession={() => { createNewSession(); setSidebarOpen(false); }}
        onDeleteSession={deleteSession}
      />

      {/* ── Main content pane ── */}
      <div className="main-pane">
        {/* Top header bar */}
        <header className="top-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {/* Mobile hamburger — show sidebar on mobile */}
            <button
              className="icon-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{ display: 'none' }}
              id="mobile-menu-btn"
            >
              <PanelLeftOpen size={18} />
            </button>
          </div>
        </header>

        {/* Scrollable messages area */}
        <div className="messages-scroll">
          <div className="messages-container">
            {!hasMessages ? (
              <div className="empty-state">
                <div className="empty-state-icon">
                  <Sparkles size={24} />
                </div>
                <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
                  What can I help with?
                </h2>
                <p style={{ color: 'var(--text-tertiary)', fontSize: 14, maxWidth: 380 }}>
                  Ask about real-time weather, flight options, or eco-friendly travel routing.
                </p>
              </div>
            ) : (
              activeSession.messages.map(msg => (
                <ChatMessage key={msg.id} message={msg} />
              ))
            )}
            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Floating input bar */}
        <ChatInput
          onSendMessage={sendMessage}
          onStopStreaming={stopStreaming}
          isStreaming={isStreaming}
          showSuggestions={!hasMessages}
        />
      </div>
    </div>
  );
}

export default App;

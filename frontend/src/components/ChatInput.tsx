import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Square, Compass, CloudSun, Plane, MapPin } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  onStopStreaming: () => void;
  isStreaming: boolean;
  disabled?: boolean;
  showSuggestions?: boolean;
}

const SUGGESTIONS = [
  { icon: <CloudSun size={16} style={{ color: '#fbbf24' }} />, title: 'Weather in Saskatoon', sub: 'Check current weather & hourly forecast' },
  { icon: <Plane size={16} style={{ color: '#a78bfa' }} />, title: 'Flight Options', sub: 'Find flights from Vancouver to Calgary' },
  { icon: <Compass size={16} style={{ color: '#60a5fa' }} />, title: 'Ground Travel Route', sub: 'Driving route from Toronto to Montreal' },
  { icon: <MapPin size={16} style={{ color: '#10b981' }} />, title: 'Nearest Airport', sub: 'Find closest airport to Saskatoon, SK' },
];

/**
 * Floating chat input bar with auto-resizing textarea,
 * prompt suggestion cards, and streaming stop control.
 */
export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStopStreaming,
  isStreaming,
  disabled,
  showSuggestions
}) => {
  const [text, setText] = useState('');
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'auto';
      ref.current.style.height = `${Math.min(ref.current.scrollHeight, 150)}px`;
    }
  }, [text]);

  const submit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!text.trim() || isStreaming || disabled) return;
    onSendMessage(text.trim());
    setText('');
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const canSend = text.trim().length > 0 && !disabled;

  return (
    <div className="input-area">
      {/* Suggestion cards on empty state */}
      {showSuggestions && (
        <div className="suggestions-grid">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} className="suggestion-card" onClick={() => onSendMessage(`${s.title}: ${s.sub}`)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                {s.icon}
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{s.title}</span>
              </div>
              <p style={{ fontSize: 11, color: 'var(--text-tertiary)', margin: 0 }}>{s.sub}</p>
            </button>
          ))}
        </div>
      )}

      {/* Input pill */}
      <form onSubmit={submit} className="input-pill">
        <textarea
          ref={ref}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask Greenway AI…"
          rows={1}
          disabled={disabled}
        />

        {isStreaming ? (
          <button type="button" className="send-btn active" onClick={onStopStreaming} title="Stop">
            <Square size={14} fill="#09090b" />
          </button>
        ) : (
          <button type="submit" className={`send-btn ${canSend ? 'active' : 'disabled'}`} disabled={!canSend}>
            <ArrowUp size={16} strokeWidth={2.5} />
          </button>
        )}
      </form>

      <p className="input-disclaimer">
        Greenway AI can make mistakes. Verify travel & weather details.
      </p>
    </div>
  );
};

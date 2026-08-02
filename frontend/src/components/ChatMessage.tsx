import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../types/chat';
import { ToolAccordion } from './ToolAccordion';
import { Sparkles, Copy, Check } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

/**
 * Renders a single chat message — user bubbles on the right,
 * assistant responses (with tool accordions and markdown) on the left.
 */
export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  /* ── User message ── */
  if (message.role === 'user') {
    return (
      <div className="user-message-row">
        <div className="user-bubble">{message.content}</div>
      </div>
    );
  }

  /* ── Assistant message ── */
  return (
    <div className="assistant-message-row">
      <div className="assistant-avatar">
        <Sparkles size={16} />
      </div>

      <div className="assistant-content">
        {/* Tool execution accordions */}
        {message.tools && message.tools.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            {message.tools.map(tool => (
              <ToolAccordion key={tool.id} tool={tool} />
            ))}
          </div>
        )}

        {/* Markdown content stream */}
        <div className="prose">
          {message.content ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          ) : message.isStreaming ? (
            <span style={{ color: 'var(--text-dim)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
              Thinking…
            </span>
          ) : null}

          {message.isStreaming && message.content && (
            <span className="cursor-blink" />
          )}
        </div>

        {/* Copy action toolbar — visible on hover */}
        {message.content && !message.isStreaming && (
          <div className="action-toolbar">
            <button className="action-btn" onClick={handleCopy} title="Copy response">
              {copied ? (
                <><Check size={13} style={{ color: 'var(--accent)' }} /><span style={{ color: 'var(--accent)' }}>Copied</span></>
              ) : (
                <><Copy size={13} /><span>Copy</span></>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

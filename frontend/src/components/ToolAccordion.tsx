import React, { useState } from 'react';
import type { ToolExecution } from '../types/chat';
import { Loader2, Check, ChevronRight, Wrench, Search, MapPin, CloudSun, Route, Plane } from 'lucide-react';

interface ToolAccordionProps {
  tool: ToolExecution;
}

/**
 * Collapsible tool execution accordion showing live status
 * and expandable input/output details.
 */
export const ToolAccordion: React.FC<ToolAccordionProps> = ({ tool }) => {
  const [isOpen, setIsOpen] = useState(false);

  const iconMap: Record<string, React.ReactNode> = {
    web_search: <Search size={13} style={{ color: '#22d3ee' }} />,
    geocode: <MapPin size={13} style={{ color: '#10b981' }} />,
    get_nearest_airport: <MapPin size={13} style={{ color: '#10b981' }} />,
    get_weather_current: <CloudSun size={13} style={{ color: '#fbbf24' }} />,
    get_weather_forecast: <CloudSun size={13} style={{ color: '#fbbf24' }} />,
    get_weather_hourly: <CloudSun size={13} style={{ color: '#fbbf24' }} />,
    get_ground_route: <Route size={13} style={{ color: '#60a5fa' }} />,
    get_flight_options: <Plane size={13} style={{ color: '#a78bfa' }} />,
  };

  const icon = iconMap[tool.name] || <Wrench size={13} style={{ color: 'var(--text-tertiary)' }} />;

  const label = tool.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  return (
    <div style={{ marginBottom: 6 }}>
      <button
        className="tool-accordion-btn"
        onClick={() => tool.output && setIsOpen(!isOpen)}
        disabled={!tool.output}
      >
        {tool.status === 'running' ? (
          <Loader2 size={14} style={{ color: 'var(--accent)', animation: 'spin 1s linear infinite' }} />
        ) : (
          <div style={{
            width: 18, height: 18, borderRadius: '50%',
            background: 'var(--accent-dim)', border: '1px solid rgba(16,185,129,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Check size={11} style={{ color: 'var(--accent)' }} />
          </div>
        )}

        {icon}

        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 500 }}>
          {tool.status === 'running' ? `Running ${label}…` : label}
        </span>

        {tool.output && (
          <ChevronRight
            size={13}
            style={{
              marginLeft: 'auto',
              color: 'var(--text-dim)',
              transition: 'transform 0.2s',
              transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)'
            }}
          />
        )}
      </button>

      {isOpen && tool.output && (
        <div className="tool-accordion-output">
          {tool.input && (
            <div style={{ marginBottom: 8, paddingBottom: 8, borderBottom: '1px solid var(--border-default)', color: 'var(--text-tertiary)' }}>
              <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Input</span>
              <pre style={{ marginTop: 4 }}>{tool.input}</pre>
            </div>
          )}
          <div>
            <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600, color: 'var(--text-tertiary)' }}>Output</span>
            <pre style={{ marginTop: 4, color: 'var(--text-secondary)' }}>{tool.output}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

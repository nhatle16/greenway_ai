/**
 * Defines conversation roles: user prompt vs assistant completion.
 */
export type Role = 'user' | 'assistant';

/**
 * Represents an individual tool execution invoked by the agent (e.g. web search, weather check).
 */
export interface ToolExecution {
  id: string;
  name: string;
  input?: string;
  output?: string;
  status: 'running' | 'completed' | 'failed';
  timestamp: number;
}

/**
 * Represents a single chat message in the conversation trajectory.
 */
export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: number;
  tools?: ToolExecution[];
  isStreaming?: boolean;
}

/**
 * Represents a persistent conversation session corresponding to a thread_id.
 */
export interface ChatSession {
  id: string;
  title: string;
  createdAt: number;
  messages: Message[];
}

/**
 * Server-Sent Event (SSE) payload structures returned by /api/chat/stream.
 */
export type StreamEvent =
  | { type: 'meta'; thread_id: string | null }
  | { type: 'stream'; content: string }
  | { type: 'tool_start'; tool: string; input?: string }
  | { type: 'tool_end'; tool: string; output?: string }
  | { type: 'done'; thread_id: string | null }
  | { type: 'error'; detail: string };


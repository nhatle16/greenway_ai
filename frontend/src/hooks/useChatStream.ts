import { useState, useEffect, useRef, useCallback } from 'react';
import type { Message, ChatSession, ToolExecution, StreamEvent } from '../types/chat';

const SESSIONS_STORAGE_KEY = 'greenway_chat_sessions';
const ACTIVE_THREAD_KEY = 'greenway_active_thread_id';

/**
 * Custom React hook for managing SSE chat streaming, thread sessions, and backend connection health.
 */
export function useChatStream() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  
  // Ref holding AbortController to allow users to cancel ongoing streams
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load saved sessions on startup
  useEffect(() => {
    try {
      const savedSessions = localStorage.getItem(SESSIONS_STORAGE_KEY);
      const savedThreadId = localStorage.getItem(ACTIVE_THREAD_KEY);
      
      if (savedSessions) {
        const parsed: ChatSession[] = JSON.parse(savedSessions);
        setSessions(parsed);
        if (savedThreadId && parsed.some(s => s.id === savedThreadId)) {
          setActiveThreadId(savedThreadId);
        } else if (parsed.length > 0) {
          setActiveThreadId(parsed[0].id);
        }
      } else {
        createNewSession();
      }
    } catch {
      createNewSession();
    }
  }, []);

  // Save sessions to localStorage
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(sessions));
    }
    if (activeThreadId) {
      localStorage.setItem(ACTIVE_THREAD_KEY, activeThreadId);
    }
  }, [sessions, activeThreadId]);



  const activeSession = sessions.find(s => s.id === activeThreadId) || null;

  const createNewSession = useCallback(() => {
    const newSession: ChatSession = {
      id: 'thread-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5),
      title: 'New Conversation',
      createdAt: Date.now(),
      messages: []
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveThreadId(newSession.id);
    return newSession.id;
  }, []);

  const deleteSession = useCallback((threadId: string) => {
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== threadId);
      if (filtered.length === 0) {
        const newId = 'thread-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
        const newSession: ChatSession = {
          id: newId,
          title: 'New Conversation',
          createdAt: Date.now(),
          messages: []
        };
        setActiveThreadId(newId);
        return [newSession];
      }
      if (activeThreadId === threadId) {
        setActiveThreadId(filtered[0].id);
      }
      return filtered;
    });
  }, [activeThreadId]);

  const sendMessage = async (promptText: string) => {
    if (!promptText.trim() || isStreaming) return;

    let currentThreadId = activeThreadId;
    if (!currentThreadId) {
      currentThreadId = createNewSession();
    }

    const userMessageId = 'msg-' + Date.now();
    const userMessage: Message = {
      id: userMessageId,
      role: 'user',
      content: promptText,
      timestamp: Date.now()
    };

    const assistantMessageId = 'msg-' + (Date.now() + 1);
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      tools: [],
      isStreaming: true
    };

    // Update state with user prompt and initial empty assistant message
    setSessions(prev =>
      prev.map(s => {
        if (s.id === currentThreadId) {
          const isFirstMessage = s.messages.length === 0;
          return {
            ...s,
            title: isFirstMessage ? promptText.slice(0, 30) + (promptText.length > 30 ? '...' : '') : s.title,
            messages: [...s.messages, userMessage, assistantMessage]
          };
        }
        return s;
      })
    );

    setIsStreaming(true);
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: promptText,
          thread_id: currentThreadId
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok || !response.body) {
        throw new Error(`HTTP Error ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // keep remaining partial line in buffer

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;

          const jsonStr = trimmed.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const event: StreamEvent = JSON.parse(jsonStr);

            setSessions(prev =>
              prev.map(session => {
                if (session.id !== currentThreadId) return session;

                const messages = session.messages.map(msg => {
                  if (msg.id !== assistantMessageId) return msg;

                  let updatedContent = msg.content;
                  let updatedTools = [...(msg.tools || [])];

                  if (event.type === 'stream') {
                    updatedContent += event.content;
                  } else if (event.type === 'tool_start') {
                    const toolExec: ToolExecution = {
                      id: 'tool-' + Date.now() + '-' + Math.random().toString(36).substr(2, 4),
                      name: event.tool,
                      input: event.input,
                      status: 'running',
                      timestamp: Date.now()
                    };
                    updatedTools.push(toolExec);
                  } else if (event.type === 'tool_end') {
                    const idx = updatedTools.findIndex(t => t.name === event.tool && t.status === 'running');
                    if (idx !== -1) {
                      updatedTools[idx] = {
                        ...updatedTools[idx],
                        output: event.output,
                        status: 'completed'
                      };
                    }
                  } else if (event.type === 'error') {
                    updatedContent += `\n\n*Error: ${event.detail}*`;
                  }

                  return {
                    ...msg,
                    content: updatedContent,
                    tools: updatedTools,
                    isStreaming: event.type !== 'done' && event.type !== 'error'
                  };
                });

                return { ...session, messages };
              })
            );
          } catch {
            // Ignore malformed SSE lines
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setSessions(prev =>
          prev.map(session => {
            if (session.id !== currentThreadId) return session;
            return {
              ...session,
              messages: session.messages.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: msg.content + `\n\n*Connection error: ${err.message}*`, isStreaming: false }
                  : msg
              )
            };
          })
        );
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
      // Mark assistant message streaming as finished
      setSessions(prev =>
        prev.map(session => {
          if (session.id !== currentThreadId) return session;
          return {
            ...session,
            messages: session.messages.map(msg =>
              msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg
            )
          };
        })
      );
    }
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  };

  return {
    sessions,
    activeThreadId,
    activeSession,
    isStreaming,
    setActiveThreadId,
    createNewSession,
    deleteSession,
    sendMessage,
    stopStreaming
  };
}

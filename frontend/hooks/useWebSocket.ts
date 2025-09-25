
import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketStatus } from '../types';
import type { WebSocketMessage } from '../types';
import { RECONNECT_DELAY_MS } from '../constants';

export const useWebSocket = (url: string, onMessage: (message: WebSocketMessage) => void): WebSocketStatus => {
  const [status, setStatus] = useState<WebSocketStatus>(WebSocketStatus.CONNECTING);
  const ws = useRef<WebSocket | null>(null);
  // FIX: Replaced NodeJS.Timeout with ReturnType<typeof setTimeout> for browser compatibility.
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus(WebSocketStatus.CONNECTING);
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setStatus(WebSocketStatus.CONNECTED);
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus(WebSocketStatus.ERROR);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setStatus(WebSocketStatus.DISCONNECTED);
      // Simple reconnect logic
      if (!reconnectTimeout.current) {
          reconnectTimeout.current = setTimeout(() => {
              console.log('Attempting to reconnect...');
              connect();
          }, RECONNECT_DELAY_MS);
      }
    };
  }, [url, onMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
     // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connect]);

  return status;
};

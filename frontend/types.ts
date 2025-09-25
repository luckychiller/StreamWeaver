
export enum WebSocketStatus {
  CONNECTING = 'CONNECTING',
  CONNECTED = 'CONNECTED',
  DISCONNECTED = 'DISCONNECTED',
  ERROR = 'ERROR',
}

export interface StockTradePayload {
  timestamp: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
}

export interface SocialPostPayload {
  timestamp: string;
  user: string;
  post_id: string;
  content: string;
  hashtags: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
}

export interface ServerLogPayload {
  timestamp: string;
  service: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  message: string;
  ip: string;
}

export type WebSocketMessage =
  | { type: 'stock_trade'; payload: StockTradePayload }
  | { type: 'social_post'; payload: SocialPostPayload }
  | { type: 'server_log'; payload: ServerLogPayload };

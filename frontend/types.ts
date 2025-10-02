
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

export interface TrafficDataPayload {
  timestamp: string;
  location_id: string;
  vehicle_count: number;
  average_speed: number;
  congestion_level: 'light' | 'moderate' | 'heavy' | 'severe';
  direction: 'northbound' | 'southbound' | 'eastbound' | 'westbound';
  occupancy_rate: number;
  headway_seconds: number;
  weather_condition: string;
  visibility_miles: number;
  precipitation_inches: number;
}

export type WebSocketMessage =
  | { type: 'stock_trade'; payload: StockTradePayload }
  | { type: 'social_post'; payload: SocialPostPayload }
  | { type: 'server_log'; payload: ServerLogPayload }
  | { type: 'traffic_data'; payload: TrafficDataPayload };

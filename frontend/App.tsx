import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import Header from './components/Header';
import StockTradesPanel from './components/StockTradesPanel';
import SocialFeedPanel from './components/SocialFeedPanel';
import ServerLogsPanel from './components/ServerLogsPanel';
import TrafficDataPanel from './components/TrafficDataPanel';
import { MAX_STOCK_TRADES, MAX_SOCIAL_POSTS, MAX_SERVER_LOGS, MAX_TRAFFIC_DATA, WEBSOCKET_URL } from './constants';
import type { WebSocketMessage, StockTradePayload, SocialPostPayload, ServerLogPayload, TrafficDataPayload } from './types';

const App: React.FC = () => {
  const [stockTrades, setStockTrades] = useState<StockTradePayload[]>([]);
  const [socialPosts, setSocialPosts] = useState<SocialPostPayload[]>([]);
  const [serverLogs, setServerLogs] = useState<ServerLogPayload[]>([]);
  const [trafficData, setTrafficData] = useState<TrafficDataPayload[]>([]);
  const [messageCount, setMessageCount] = useState(0);
  const [dataRate, setDataRate] = useState(0);
  const messageCountRef = useRef(0);

  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'stock_trade':
        setStockTrades(prev => [message.payload, ...prev].slice(0, MAX_STOCK_TRADES));
        break;
      case 'social_post':
        setSocialPosts(prev => [message.payload, ...prev].slice(0, MAX_SOCIAL_POSTS));
        break;
      case 'server_log':
        setServerLogs(prev => [message.payload, ...prev].slice(0, MAX_SERVER_LOGS));
        break;
      case 'traffic_data':
        setTrafficData(prev => [message.payload, ...prev].slice(0, MAX_TRAFFIC_DATA));
        break;
    }
    messageCountRef.current += 1;
  }, []);

  const connectionStatus = useWebSocket(WEBSOCKET_URL, handleWebSocketMessage);

  useEffect(() => {
    const interval = setInterval(() => {
      setDataRate(messageCountRef.current);
      messageCountRef.current = 0;
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen">
      <Header status={connectionStatus} dataRate={dataRate} />
      <main className="p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <StockTradesPanel trades={stockTrades} />
          </div>
          <div className="xl:col-span-1">
            <SocialFeedPanel posts={socialPosts} />
          </div>
          <div className="xl:col-span-3">
            <TrafficDataPanel trafficData={trafficData} />
          </div>
          <div className="xl:col-span-3">
            <ServerLogsPanel logs={serverLogs} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
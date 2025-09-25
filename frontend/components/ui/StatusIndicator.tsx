import React from 'react';
import { WebSocketStatus } from '../../types';

interface StatusIndicatorProps {
  status: WebSocketStatus;
}

const statusConfig = {
  [WebSocketStatus.CONNECTED]: { color: 'bg-green-500', text: 'Connected' },
  [WebSocketStatus.CONNECTING]: { color: 'bg-yellow-500', text: 'Connecting...' },
  [WebSocketStatus.DISCONNECTED]: { color: 'bg-red-500', text: 'Disconnected' },
  [WebSocketStatus.ERROR]: { color: 'bg-red-700', text: 'Error' },
};

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
  const { color, text } = statusConfig[status];

  return (
    <div className="flex items-center space-x-2 text-sm text-green-400/80">
      <span className={`relative flex h-3 w-3`}>
        <span className={`animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite] absolute inline-flex h-full w-full rounded-full ${color} opacity-75`}></span>
        <span className={`relative inline-flex rounded-full h-3 w-3 ${color}`}></span>
      </span>
      <span>{text}</span>
    </div>
  );
};

export default React.memo(StatusIndicator);
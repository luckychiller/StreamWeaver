import React from 'react';
import { WebSocketStatus } from '../types';
import StatusIndicator from './ui/StatusIndicator';

interface HeaderProps {
  status: WebSocketStatus;
  dataRate: number;
}

const Header: React.FC<HeaderProps> = ({ status, dataRate }) => {
  return (
    <header className="px-4 py-2 border-b border-green-500/30 bg-black/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
            <svg className="w-8 h-8 text-green-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            <h1 className="text-xl sm:text-2xl font-bold text-green-400 tracking-tight text-glow">
                Streamweaver Dashboard
            </h1>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <span className="text-xs text-green-600 block">Data Rate</span>
            <span className="text-lg font-bold text-lime-300">
              {dataRate} msg/s
            </span>
          </div>
          <StatusIndicator status={status} />
        </div>
      </div>
    </header>
  );
};

export default React.memo(Header);
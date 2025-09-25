import React, { useRef, useEffect, useMemo } from 'react';
import Card from './ui/Card';
import type { ServerLogPayload } from '../types';
import { formatTimestamp } from '../utils/time';
import { ERROR_LOG_TIMEFRAME_MS } from '../constants';

const logLevelConfig = {
  ERROR: 'bg-red-500/20 text-red-400 border-red-500/30',
  WARN: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  INFO: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  DEBUG: 'bg-gray-500/20 text-gray-500 border-gray-500/30',
};

const LogEntry: React.FC<{ log: ServerLogPayload }> = ({ log }) => {
  const colorClasses = logLevelConfig[log.level] || logLevelConfig.DEBUG;
  return (
    <div className="grid grid-cols-[auto,auto,1fr] items-baseline gap-x-3 font-mono text-sm leading-tight">
      <span className="text-green-900">{formatTimestamp(log.timestamp)}</span>
      <span className={`px-2 rounded-sm text-xs font-bold border ${colorClasses}`}>
        {log.level}
      </span>
      <span className="text-green-400 whitespace-pre-wrap break-all">{log.message}</span>
    </div>
  );
};

interface ServerLogsPanelProps {
  logs: ServerLogPayload[];
}

const ServerLogsPanel: React.FC<ServerLogsPanelProps> = ({ logs }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  const errorCount = useMemo(() => {
    const oneMinuteAgo = Date.now() - ERROR_LOG_TIMEFRAME_MS;
    return logs.filter(log => log.level === 'ERROR' && new Date(log.timestamp).getTime() > oneMinuteAgo).length;
  }, [logs]);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <Card className="h-full flex flex-col">
      <div className="p-4 border-b border-green-900 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-green-300 uppercase tracking-widest text-glow">
            Live Server Logs<span className="animate-pulse">_</span>
        </h2>
        <div className="text-right">
            <span className="text-xs text-green-600 block">Errors (last 1m)</span>
            <span className={`text-xl font-bold ${errorCount > 0 ? 'text-red-500 text-glow' : 'text-green-500'}`}>
              {errorCount}
            </span>
          </div>
      </div>
      <div ref={scrollContainerRef} className="flex-grow p-4 overflow-y-auto h-96 space-y-2">
        {logs.map(log => <LogEntry key={`${log.timestamp}-${log.service}`} log={log} />).reverse()}
      </div>
    </Card>
  );
};

export default React.memo(ServerLogsPanel);
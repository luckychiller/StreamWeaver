import React, { useMemo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import Card from './ui/Card';
import type { StockTradePayload } from '../types';
import { formatTimestamp } from '../utils/time';

interface StockTradesPanelProps {
  trades: StockTradePayload[];
}

const StockTradesPanel: React.FC<StockTradesPanelProps> = ({ trades }) => {
  const latestPrices = useMemo(() => {
    const prices: { [symbol: string]: number } = {};
    trades.forEach(trade => {
      prices[trade.symbol] = trade.price;
    });
    return Object.entries(prices).map(([symbol, price]) => ({ symbol, price }));
  }, [trades]);

  const chartData = useMemo(() => {
    return latestPrices.map(item => ({
      symbol: item.symbol,
      price: item.price,
    }));
  }, [latestPrices]);

  const recentTrades = useMemo(() => trades.slice(0, 8), [trades]);

  return (
    <Card className="h-full flex flex-col">
      <div className="p-4 border-b border-green-900">
        <h2 className="text-lg font-semibold text-green-300 uppercase tracking-widest text-glow">
          Real-time Stock Prices<span className="animate-pulse">_</span>
        </h2>
      </div>
      <div className="flex-grow h-64 md:h-80 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(22, 163, 74, 0.2)" />
            <XAxis
              dataKey="symbol"
              stroke="#34d399"
              fontSize={12}
              tick={{ fill: '#34d399' }}
            />
            <YAxis
              stroke="#34d399"
              fontSize={12}
              tickFormatter={(price) => `$${price.toFixed(2)}`}
              tick={{ fill: '#34d399' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#000',
                borderColor: '#166534',
                color: '#84cc16'
              }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
            />
            <Bar dataKey="price" fill="#84cc16" />
          </BarChart>
        </ResponsiveContainer>
      </div>
       <div className="p-4 border-t border-green-900">
        <h3 className="text-sm font-semibold text-green-300 uppercase mb-2">Recent Trades</h3>
        <div className="text-xs text-green-500 grid grid-cols-5 gap-2">
            <div className="text-green-600">Time</div>
            <div className="text-green-600">Symbol</div>
            <div className="text-green-600">Type</div>
            <div className="text-green-600 text-right">Price</div>
            <div className="text-green-600 text-right">Quantity</div>
            {recentTrades.map(trade => (
                <React.Fragment key={`${trade.timestamp}-${trade.symbol}`}>
                    <div>{formatTimestamp(trade.timestamp)}</div>
                    <div>{trade.symbol}</div>
                    <div className={trade.type === 'BUY' ? 'text-lime-400' : 'text-red-500'}>{trade.type}</div>
                    <div className="text-right">${trade.price.toFixed(2)}</div>
                    <div className="text-right">{trade.quantity}</div>
                </React.Fragment>
            ))}
        </div>
      </div>
    </Card>
  );
};

export default React.memo(StockTradesPanel);
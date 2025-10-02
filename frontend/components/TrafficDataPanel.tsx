import React, { useMemo } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import Card from './ui/Card';
import type { TrafficDataPayload } from '../types';
import { formatTimestamp } from '../utils/time';

interface TrafficDataPanelProps {
  trafficData: TrafficDataPayload[];
}

const TrafficDataPanel: React.FC<TrafficDataPanelProps> = ({ trafficData }) => {
  const chartData = useMemo(() => {
    return trafficData.slice(0, 20).map(data => ({
      timestamp: formatTimestamp(data.timestamp),
      vehicle_count: data.vehicle_count,
      average_speed: data.average_speed,
      occupancy_rate: data.occupancy_rate,
    }));
  }, [trafficData]);

  const recentData = useMemo(() => trafficData.slice(0, 8), [trafficData]);

  const getCongestionColor = (level: string) => {
    switch (level) {
      case 'light': return 'text-green-400';
      case 'moderate': return 'text-yellow-400';
      case 'heavy': return 'text-orange-400';
      case 'severe': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getSpeedColor = (speed: number) => {
    if (speed > 60) return 'text-green-400';
    if (speed > 30) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <Card className="h-full flex flex-col">
      <div className="p-4 border-b border-blue-900">
        <h2 className="text-lg font-semibold text-blue-300 uppercase tracking-widest text-glow">
          Real-time Traffic Data<span className="animate-pulse">_</span>
        </h2>
      </div>
      <div className="flex-grow h-64 md:h-80 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(59, 130, 246, 0.2)" />
            <XAxis
              dataKey="timestamp"
              stroke="#3b82f6"
              fontSize={10}
              tick={{ fill: '#3b82f6' }}
            />
            <YAxis
              yAxisId="left"
              stroke="#3b82f6"
              fontSize={12}
              tick={{ fill: '#3b82f6' }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#10b981"
              fontSize={12}
              tick={{ fill: '#10b981' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#000',
                borderColor: '#1e3a8a',
                color: '#60a5fa'
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="vehicle_count"
              stroke="#60a5fa"
              strokeWidth={2}
              name="Vehicle Count"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="average_speed"
              stroke="#10b981"
              strokeWidth={2}
              name="Avg Speed (mph)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="p-4 border-t border-blue-900">
        <h3 className="text-sm font-semibold text-blue-300 uppercase mb-2">Recent Traffic Data</h3>
        <div className="text-xs text-blue-500 grid grid-cols-6 gap-1">
          <div className="text-blue-600">Time</div>
          <div className="text-blue-600">Location</div>
          <div className="text-blue-600">Vehicles</div>
          <div className="text-blue-600">Speed</div>
          <div className="text-blue-600">Congestion</div>
          <div className="text-blue-600">Weather</div>
          {recentData.map((data, index) => (
            <React.Fragment key={`${data.timestamp}-${data.location_id}-${index}`}>
              <div className="truncate">{formatTimestamp(data.timestamp)}</div>
              <div className="truncate capitalize">{data.location_id.replace('_', ' ')}</div>
              <div className="text-cyan-400">{data.vehicle_count}</div>
              <div className={getSpeedColor(data.average_speed)}>{data.average_speed.toFixed(1)} mph</div>
              <div className={getCongestionColor(data.congestion_level)}>{data.congestion_level}</div>
              <div className="truncate text-purple-400">{data.weather_condition}</div>
            </React.Fragment>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default React.memo(TrafficDataPanel);
import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import Card from './ui/Card';
import type { SocialPostPayload } from '../types';
import { formatRelativeTime } from '../utils/time';

const sentimentConfig = {
    positive: 'bg-green-500',
    neutral: 'bg-gray-500',
    negative: 'bg-red-500',
};

const COLORS = ['#84cc16', '#6b7280', '#dc2626'];

const SocialPostCard: React.FC<{ post: SocialPostPayload }> = ({ post }) => {
    const sentimentColor = sentimentConfig[post.sentiment];
    return (
        <div className="p-2 border-b border-green-900 last:border-b-0 animate-fade-in">
            <div className="flex justify-between items-start mb-1">
                <div className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${sentimentColor}`}></span>
                    <p className="font-bold text-sm text-lime-400">{post.user}</p>
                </div>
                <p className="text-xs text-green-700">{formatRelativeTime(post.timestamp)}</p>
            </div>
            <p className="text-sm text-green-400 mb-2">{post.content}</p>
            <div className="flex flex-wrap gap-x-3 gap-y-1">
                {post.hashtags.map(tag => (
                    <span key={tag} className="text-xs text-cyan-400 hover:underline cursor-pointer">
                        {tag}
                    </span>
                ))}
            </div>
        </div>
    )
}

interface SocialFeedPanelProps {
  posts: SocialPostPayload[];
}

const SocialFeedPanel: React.FC<SocialFeedPanelProps> = ({ posts }) => {
  const sentimentData = useMemo(() => {
    const counts = { positive: 0, neutral: 0, negative: 0 };
    posts.forEach(post => {
      counts[post.sentiment]++;
    });
    return [
      { name: 'Positive', value: counts.positive, color: '#84cc16' },
      { name: 'Neutral', value: counts.neutral, color: '#6b7280' },
      { name: 'Negative', value: counts.negative, color: '#dc2626' },
    ];
  }, [posts]);

  return (
    <Card className="h-full flex flex-col">
      <div className="p-4 border-b border-green-900">
        <h2 className="text-lg font-semibold text-green-300 uppercase tracking-widest text-glow">
            Social Media Feed<span className="animate-pulse">_</span>
        </h2>
      </div>
      <div className="flex-grow flex">
        <div className="w-1/2 p-4">
          <h3 className="text-sm font-semibold text-green-300 mb-2">Sentiment Analysis</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="w-1/2 flex-grow overflow-y-auto h-96">
          {posts.map(post => <SocialPostCard key={post.post_id} post={post} />)}
        </div>
      </div>
    </Card>
  );
};

export default React.memo(SocialFeedPanel);
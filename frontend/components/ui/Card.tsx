import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-black/50 border border-green-900 rounded-none ${className}`}>
      {children}
    </div>
  );
};

export default Card;